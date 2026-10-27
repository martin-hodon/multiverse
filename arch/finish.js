// FINISHES: what a building's surfaces are made of -- its floors, its walls inside and out, its ceilings and vaults, its
// roofs -- as RULES over the assembled building (assets/finishes/<building>.json), and the texture coordinates each
// surface is patterned by. The patterns themselves are patterns.js; the game's material is architecture.js.
//
// A rule is what it matches and what it gives, and the FIRST rule that matches a piece of surface wins:
//   match   parts: a part's name (its name less a trailing number, its own name inside a component, the component's
//                  name) or "kind:<kind>", one or a list
//           surface: floor | wall | ceiling | roof     side: in | out
//           below / above: a height (the building's frame, 0 at the ground)     within: [x0, z0, x1, z1] on the plan
//           reveal: true -- only an opening's REVEAL (its jambs, its sill, its soffit: a face of a wall or a ring's bay
//                  turned square to the wall's own face), false -- never one (a drum's deep oculi, plain in a panelled face)
//   gives   pattern: "family/name", palette, scale (of its tile), turn (degrees), map, align, offset, params, res
//           at: [x, z] (a panel, centred there)  fit: [x0, z0, x1, z1] (a panel made to that size: its params W, H)
//           count: how many tiles round a revolved surface (else as many as fit)
//           -- or a plain stone: color, accent, pat (the old tile patterns: ashlar, marble, tiles...)
// What no rule matches is the building's `stone`.
//
// SURFACE is read from the triangle: up-facing (n.y >= .7) a floor, down-facing a ceiling, else a wall; on a roof or a
// dome, its outside is its roof. SIDE is read from the stone around it, FACE by face (facesOf, bandsOf): how open the
// air the surface faces is -- sky straight over it, or a sixth of evenly spread directions escaping the building -- in
// level bands up each face, a reveal following the wall it pierces. (docs/patterns.md: the whole of it.)
//   A floor that runs from inside to outside (a platform under a church and before its door) is one plane of a few
// large triangles, so large floors are cut on a 2m grid before they are classified; bands (below/above) and regions
// (within, panels) cut what crosses their lines. The cuts are made from the edge's own ends in one order, so two
// triangles sharing an edge cut it at the same point.
//
// MAPPING -- the pattern's (u, v), in metres: `plan` (a floor, a ceiling: u east, v north), `face` (a wall: u along it,
// v up), `revolve` (a dome, a drum, a column, a round roof: u round the part's own axis -- a whole number of tiles round,
// so the rows meet -- and v up the meridian's length on a dome), `slope` (a roof: u along the eave, v up the slope).
// By kind unless the rule says. `align: "part"` sets the tile's foot on the part's foot (a painted beam, a band).
import { rayIndex, rayHits, rayDist, insideOf } from "./solid.js";

// a part's names, most particular first: its name, its name less a trailing number ("aisle roof 3"), its own name inside
// a component, the component's name, its kind (architecture.js reads a building's colours by the same list)
export const partNames = (p) => [p.name, p.name.replace(/ \d+$/, ""), p.name.split("/").pop(), p.name.split("/")[0], "kind:" + p.kind];
const FLOORLESS = new Set(["roof", "dome", "vault", "groin", "ribs", "pendentives"]);     // (their tops are roofs, not floors)
const ROOFY = new Set(["roof", "dome"]);
// TRIM: a moulding run along a face (a course, a wimperg) is ONE material over all its faces -- its weathered top, its
// drip, its corona's front -- the outside wall's, or what a rule gives it: never a floor's pattern on its top and the
// wall's on its front. Every face of it is a wall, outside.
const TRIM = new Set(["moulding", "wimperg"]);
const STAIRS = new Set(["flight", "staircase", "steps", "spiral-stair", "crepidoma", "base"]);

// ---- inside or out -------------------------------------------------------------------------------------------------
const TAU = Math.PI * 2, UP = [0, 1, 0];
const dirAt = (az, el) => [Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)];
const RING = (el, n) => Array.from({ length: n }, (_, k) => dirAt(k * TAU / n, el));
const STEEP = RING(.9, 3), SKYWARD = RING(.8, 8);
// sixteen directions spread evenly over a half of space (Fibonacci), about +z
const HALF = Array.from({ length: 16 }, (_, i) => {
  const z = 1 - (i + .5) / 16, r = Math.sqrt(1 - z * z), a = i * 2.399963;
  return [r * Math.cos(a), r * Math.sin(a), z];
});
const LEVEL = RING(.03, 12);
// sixteen level directions round, at three turns a third of a step apart (one set per height a floor is asked at)
const ROUNDS = [0, 1, 2].map((i) => Array.from({ length: 16 }, (_, k) => dirAt((k + i / 3) * TAU / 16, 0)));
// twenty-four directions spread evenly over the band from level to 30 degrees up: what one standing on a floor sees
// round them -- out under a colonnade's deck, a portico's roof; in a room, only its doors (a floor is outside when a
// fifth of them escape)
const LOW = Array.from({ length: 24 }, (_, i) => { const el = Math.asin((i + .5) / 24 * .5), a = i * 2.399963; return dirAt(a, el); });
// HOW OPEN is the air a surface faces: the share of evenly spread directions in which it escapes the building. A room
// or a nave is closed but for the little its doors subtend (the Hall of Prayer's four doors: a tenth, seen from its
// middle); a portico's back wall, an arch's soffit, a drum behind its peristyle -- covered, but open sideways -- see open
// air over a sixth or more.
const OPEN = .15;
export function sideTeller(asm) {
  const tI = performance.now(), idx = rayIndex(asm), cache = new Map(), indexMs = performance.now() - tI;
  let rays = 0, rayMs = 0;
  const bySurf = {};
  // `roofy`: a roof's or a dome's face -- open to the sky above it is enough to call it outside
  const tell = (p, n, surf, roofy = false) => {
    const oct = surf === "wall" ? Math.round(Math.atan2(n[0], n[2]) / (Math.PI / 4)) & 7 : 0;
    // a wall is asked from 40cm off its face, clear of its own mouldings; a soffit from 1.5m under it, clear of the
    // capitals of the columns carrying it; a floor from where one standing on
    // it sees -- over a balcony's parapet, a terrace's balustrade (a room is closed at that height as at any)
    const off = surf === "floor" ? 1.2 : surf === "ceiling" ? 1.5 : .4, o = [p[0] + n[0] * off, p[1] + n[1] * off, p[2] + n[2] * off];
    // (an answer is shared by faces near each other facing the same way -- but only where their probes see each other:
    //  the same air. A bin's face inside a tower and the tower's own face outside, 2m apart, facing alike, are not.)
    const key = `${Math.floor(p[0] / 3)},${Math.floor(p[1] / 3)},${Math.floor(p[2] / 3)},${surf},${oct}`;
    const known = cache.get(key);
    if (known) for (const k of known) {
      const d = [k.o[0] - o[0], k.o[1] - o[1], k.o[2] - o[2]], l = Math.hypot(...d);
      if (l < 1e-6) return k.side;
      if (surf === "floor" && l > 1) continue;   // (a floor's air runs on through a doorway: a threshold sees the nave)
      rays++;
      if (!rayHits(idx, o, d.map((v) => v / l), l)) return k.side;
    }
    bySurf[surf] = (bySurf[surf] ?? 0) + 1;
    const tr = performance.now();
    const done = (side) => { rayMs += performance.now() - tr; (cache.get(key) ?? cache.set(key, []).get(key)).push({ o, side }); return side; };
    // THE SHORT WAY: sky straight over the air before it -- outside at once (a wall even in a narrow gap: a tower's face
    // toward the church it stands against); a floor must also see it steeply to the side (not only through an oculus);
    // a roof is outside if it sees the sky steeply any way at all (a taller block may stand over its straight-up ray);
    // and a floor that sees it steeply most ways round is outside though something is straight over it -- the
    // pavement at a wall's foot, under a cornice reaching out over it: three ways of eight round at 46 degrees (a
    // room's floor sees none, or one through a window or an oculus)
    if (surf !== "ceiling") {
      rays++;
      let out = !rayHits(idx, o, [0, 1, 0], 250);
      if (out && surf === "floor" && !roofy) out = STEEP.some((d) => (rays++, !rayHits(idx, o, d, 250)));
      if (!out && surf === "floor" && !roofy) out = SKYWARD.filter((d) => (rays++, !rayHits(idx, o, d, 250))).length >= 3;
      if (!out && roofy) out = STEEP.some((d) => (rays++, !rayHits(idx, o, d, 250)));
      if (out) return done("out");
    }
    // THE LONG WAY: how open the air it faces is. A floor: all round, from level to 30 degrees up; a wall: the half of
    // space before it, what of that is level or rising (below lies the ground, the building's own platform); a soffit:
    // level all round
    // A FLOOR under cover is inside when it is ENCLOSED: between it and what covers it, walls (or their glass) close
    // round it. Asked at three heights from it up to the cover (a third, a half, four fifths): inside if they close all the way round at two of them -- a
    // room's or a nave's, broken only by their doors low down (a room's door, a nave's portals; a tower's foot, its
    // belfry's open arches high over it) -- or if, taken together, under a tenth of the ways out are open. A walk
    // between buttresses, under an eave, a portico's floor, a colonnade's, a LOGGIA's -- open through its arches over
    // most of its height, closed only in the band of spandrels under its deck -- outside.
    // (Under a table, or a cover too close to look under: how open its low horizon is, below.)
    if (surf === "floor") {
      rays++;
      const up = rayDist(idx, o, [0, 1, 0], 250);
      if (up > 1 && up < Infinity) {
        const levels = [.3, .55, .8];
        // (each height turned a third of a step from the last: forty-eight ways round, not sixteen thrice -- a point
        //  lined up behind a pier of an arcade would otherwise find all three of its rows blocked by the same piers)
        let open = 0, closed = 0;
        for (const [i, f] of levels.entries()) {
          const q = [o[0], p[1] + (up + off) * f, o[2]];   // (shares of the height from the floor to its cover: a low gallery's too)
          let here = 0;
          for (const d of ROUNDS[i]) { rays++; if (!rayHits(idx, q, d, 250)) here++; }
          open += here; if (!here) closed++;
        }
        return done(closed >= 2 || open < .1 * levels.length * 16 ? "in" : "out");
      }
    }
    let dirs;
    if (surf === "ceiling") dirs = LEVEL;
    else if (surf === "floor") dirs = LOW;
    else {
      // (a frame about the normal -- for a floor, about up)
      const nn = n, h = Math.abs(nn[1]) < .9 ? [0, 1, 0] : [1, 0, 0];
      const t1 = [h[1] * nn[2] - h[2] * nn[1], h[2] * nn[0] - h[0] * nn[2], h[0] * nn[1] - h[1] * nn[0]], l1 = Math.hypot(...t1);
      const u = t1.map((q) => q / l1), v = [nn[1] * u[2] - nn[2] * u[1], nn[2] * u[0] - nn[0] * u[2], nn[0] * u[1] - nn[1] * u[0]];
      dirs = HALF.map(([x, y, z]) => [u[0] * x + v[0] * y + nn[0] * z, u[1] * x + v[1] * y + nn[1] * z, u[2] * x + v[2] * y + nn[2] * z])
                 .filter((d) => d[1] > -.05);
    }
    const need = Math.max(1, Math.ceil((surf === "floor" ? .2 : OPEN) * dirs.length));
    let open = 0, shut = 0;
    for (const d of dirs) {
      rays++;
      if (rayHits(idx, o, d, 250)) shut++; else open++;
      if (open >= need) return done("out");
      if (shut > dirs.length - need) break;
    }
    // A WALL FOUND CLOSED IN GOES AS THE FLOOR BEFORE IT, A SOFFIT AS THE FLOOR UNDER IT: the air they face is the air
    // one standing on that floor is in. A loggia's back wall and its ceiling face a cover and the piers carrying it, and
    // little sky -- but the floor of the loggia is open sideways, outside; a room's wall stands on a room's floor. So
    // a wall, its ceiling and the floor it rises from are finished as one place. (Nothing under them within reach -- a
    // wall over a void -- stays inside.)
    if (surf === "wall" || surf === "ceiling") {
      rays++;
      const dn = rayDist(idx, o, [0, -1, 0], 40);
      if (dn < Infinity) return done(tell([o[0], o[1] - dn, o[2]], UP, "floor"));
    }
    return done("in");
  };
  // is a point of a face HIDDEN: stone standing before it within `reach` (a wall or a shaft standing on a floor, a
  // column or a pier standing against a wall), or the point inside another part's solid (a shaft standing half into a
  // portal's face, an abacus's top under the deck it carries) -- a ray from inside would first meet stone far off
  tell.hidden = (q, n, own, reach) => {
    rays++;
    const o = [q[0] + n[0] * .02, q[1] + n[1] * .02, q[2] + n[2] * .02];
    if (rayHits(idx, o, n, reach)) return true;
    // (buried: stone ahead of it, and an odd count of crossings over it -- a point with open air ahead is in nothing;
    //  ahead as far as the stone goes: the foot of a column 30m tall is inside it all the way up)
    return rayHits(idx, o, n, 250) && insideOf(idx.cells, o[0], o[1], o[2], own).length > 0;
  };
  tell.stats = () => ({ rays, samples: cache.size, indexMs: Math.round(indexMs), rayMs: Math.round(rayMs), bySurf });
  return tell;
}

// ---- cutting ----------------------------------------------------------------------------------------------------------
// a convex polygon cut by the plane coordinate[axis] = c: the two sides (the point on a cut edge found from the edge's
// ends in one fixed order, so the triangle on the other side of the edge finds the same point)
function cutPoly(poly, axis, c) {
  const lo = [], hi = [];
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length], da = a[axis] - c, db = b[axis] - c;
    if (da <= 0) lo.push(a); if (da >= 0) hi.push(a);
    if ((da < 0 && db > 0) || (da > 0 && db < 0)) {
      const [p, q] = (a[0] < b[0] || (a[0] === b[0] && (a[1] < b[1] || (a[1] === b[1] && a[2] < b[2])))) ? [a, b] : [b, a];
      const t = (c - p[axis]) / (q[axis] - p[axis]), m = [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t];
      m[axis] = c;
      lo.push(m); hi.push(m);
    }
  }
  return [lo, hi].filter((q) => q.length >= 3);
}
// every cut a polygon crosses: `lines` is [[axis, c], ...]
function cutAll(poly, lines) {
  let polys = [poly];
  for (const [axis, c] of lines) {
    const next = [];
    for (const q of polys) {
      let mn = Infinity, mx = -Infinity;
      for (const v of q) { if (v[axis] < mn) mn = v[axis]; if (v[axis] > mx) mx = v[axis]; }
      if (c > mn + 1e-6 && c < mx - 1e-6) next.push(...cutPoly(q, axis, c)); else next.push(q);
    }
    polys = next;
  }
  return polys;
}

// ---- rules ------------------------------------------------------------------------------------------------------------
const listOf = (v) => v === undefined ? null : Array.isArray(v) ? v : [v];
function compile(rule, sizeOf) {
  const parts = listOf(rule.parts), surf = listOf(rule.surface), side = rule.side ?? null;
  let within = rule.within ?? null;
  // a PANEL: centred at `at` at its own size, or made to the size of `fit`
  let panel = null;
  if (rule.pattern && (rule.at || rule.fit)) {
    const [w, h] = rule.fit ? [rule.fit[2] - rule.fit[0], rule.fit[3] - rule.fit[1]] : sizeOf(rule).map((v) => v * (rule.scale ?? 1));
    const cx = rule.fit ? (rule.fit[0] + rule.fit[2]) / 2 : rule.at[0], cz = rule.fit ? (rule.fit[1] + rule.fit[3]) / 2 : rule.at[1];
    panel = { cx, cz, w, h };
    within = within ?? [cx - w / 2, cz - h / 2, cx + w / 2, cz + h / 2];
  }
  return {
    rule, panel, within,
    needsSide: !!side || (surf ?? []).includes("roof"),
    mayMatch: (names) => !parts || names.some((n) => parts.includes(n)),
    // `at` holds the piece: its names, its surface before its side is known (s0), the side (asked for only when a rule
    // needs it: casting rays is the one dear thing here) and its centre
    test(at) {
      // (a pane is finished only by a rule that names IT -- its own part, or kind:glass -- else it is glass: naming the
      //  component it belongs to (partNames' 4th, the name before the first "/") paints the walls, not their windows)
      if (parts && !at.names.some((n, i) => parts.includes(n) && !(at.glass && i === 3 && at.names[0].includes("/")))) return false;
      if (!parts && at.glass) return false;
      const c = at.cen;
      if (rule.below !== undefined && c[1] >= rule.below) return false;
      if (rule.above !== undefined && c[1] < rule.above) return false;
      if (within && (c[0] < within[0] || c[0] > within[2] || c[2] < within[1] || c[2] > within[3])) return false;
      if (rule.reveal !== undefined) {
        // (a wall's face, and a ring bay's, is its own z turned by the copy's yaw: a reveal's normal lies across that)
        const n = at.n, rev = (at.p.kind === "wall" || at.p.kind === "ring") && Math.abs(n[0] * Math.sin(at.yaw) + n[2] * Math.cos(at.yaw)) < .5;
        if (rev !== !!rule.reveal) return false;
      }
      if (surf && !surf.includes(at.surface())) return false;
      if (side && at.side() !== side) return false;
      return true;
    },
  };
}

// A PART'S FACES: its triangles joined across every edge where the surface bends by less than 25 degrees -- a wall's
// face (holes and all), a dome's skin, a vault's soffit, a roof's slope -- each of which is inside or out as a WHOLE:
// the finish belongs to the element, not to the triangles it happens to be cut into. (Worked out once a part, in its own
// frame; a copy of it only turns it.) For each face: its triangles (largest first), their centres, normals, areas and
// the heights they span.
const faceCache = new WeakMap();
function facesOf(p) {
  let F = faceCache.get(p);
  if (F) return F;
  const P = p.geometry.position, I = p.geometry.index, T = I.length / 3, nv = P.length / 3;
  const nrm = new Float32Array(T * 3), cen = new Float32Array(T * 3), area = new Float32Array(T), up = new Int32Array(T);
  for (let t = 0; t < T; t++) {
    const a = I[t * 3] * 3, b = I[t * 3 + 1] * 3, d = I[t * 3 + 2] * 3;
    const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[d] - P[a], vy = P[d + 1] - P[a + 1], vz = P[d + 2] - P[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx, l = Math.hypot(nx, ny, nz) || 1;
    nrm[t * 3] = nx / l; nrm[t * 3 + 1] = ny / l; nrm[t * 3 + 2] = nz / l; area[t] = l / 2;
    for (let q = 0; q < 3; q++) cen[t * 3 + q] = (P[a + q] + P[b + q] + P[d + q]) / 3;
    up[t] = t;
  }
  const find = (x) => { while (up[x] !== x) { up[x] = up[up[x]]; x = up[x]; } return x; };
  const edges = new Map(), COS = Math.cos(25 * Math.PI / 180), creases = [];
  for (let t = 0; t < T; t++) for (let e = 0; e < 3; e++) {
    const i = I[t * 3 + e], j = I[t * 3 + (e + 1) % 3], key = i < j ? i * nv + j : j * nv + i;
    const o = edges.get(key);
    if (o === undefined) { edges.set(key, t); continue; }
    if (nrm[t * 3] * nrm[o * 3] + nrm[t * 3 + 1] * nrm[o * 3 + 1] + nrm[t * 3 + 2] * nrm[o * 3 + 2] > COS) { const r1 = find(t), r2 = find(o); if (r1 !== r2) up[r1] = r2; }
    else creases.push(t, o);                             // (two faces meet here)
  }
  // ONE FACE IN ONE PLANE: pieces of a flat face that share no edge -- a wall's courses either side of an opening, a
  // tier's seam, the bars of a tracery, met at points that are not each other's corners -- are one face all the same
  // where they lie in one plane and touch: so they are asked once, and are inside or out together
  {
    const flat = new Map();   // (root: [normal, plane distance, box] of a face all of whose triangles face one way)
    for (let t = 0; t < T; t++) {
      const r = find(t), n = [nrm[t * 3], nrm[t * 3 + 1], nrm[t * 3 + 2]];
      let f = flat.get(r);
      if (f === undefined) flat.set(r, f = { n, ok: true, lo: [Infinity, Infinity, Infinity], hi: [-Infinity, -Infinity, -Infinity] });
      if (!f.ok) continue;
      if (n[0] * f.n[0] + n[1] * f.n[1] + n[2] * f.n[2] < .9995) { f.ok = false; continue; }
      for (let e = 0; e < 3; e++) { const i = I[t * 3 + e] * 3; for (let q = 0; q < 3; q++) { f.lo[q] = Math.min(f.lo[q], P[i + q]); f.hi[q] = Math.max(f.hi[q], P[i + q]); } }
    }
    const byPlane = new Map();
    for (const [r, f] of flat) {
      if (!f.ok) continue;
      const i = I[r * 3] * 3, d = f.n[0] * P[i] + f.n[1] * P[i + 1] + f.n[2] * P[i + 2];
      const key = f.n.map((q) => Math.round(q * 40)).join(",") + "," + Math.round(d * 20);
      (byPlane.get(key) ?? byPlane.set(key, []).get(key)).push([r, f, d]);
    }
    const E = .02;
    for (const list of byPlane.values()) for (let a = 0; a < list.length; a++) for (let b = a + 1; b < list.length; b++) {
      const [ra, fa, da] = list[a], [rb, fb, db] = list[b];
      if (Math.abs(da - db) > E || fa.n[0] * fb.n[0] + fa.n[1] * fb.n[1] + fa.n[2] * fb.n[2] < .9995) continue;
      if ([0, 1, 2].some((q) => fa.lo[q] > fb.hi[q] + E || fb.lo[q] > fa.hi[q] + E)) continue;
      const r1 = find(ra), r2 = find(rb); if (r1 !== r2) up[r1] = r2;
    }
  }
  const comp = new Int32Array(T), ids = new Map(), members = [], ylo = new Float32Array(T), yhi = new Float32Array(T);
  for (let t = 0; t < T; t++) {
    const r = find(t);
    let c = ids.get(r);
    if (c === undefined) { ids.set(r, c = members.length); members.push([]); }
    comp[t] = c; members[c].push(t);
    const ys = [P[I[t * 3] * 3 + 1], P[I[t * 3 + 1] * 3 + 1], P[I[t * 3 + 2] * 3 + 1]];
    ylo[t] = Math.min(...ys); yhi[t] = Math.max(...ys);
  }
  for (const l of members) l.sort((x, y) => area[y] - area[x]);   // (largest first: where a face is asked)
  // each face's area, and the faces it meets along a crease (a reveal meets the wall face it pierces)
  const faceArea = new Float64Array(members.length), next = members.map(() => new Set());
  for (let t = 0; t < T; t++) faceArea[comp[t]] += area[t];
  for (let q = 0; q < creases.length; q += 2) { const a = comp[creases[q]], b = comp[creases[q + 1]]; if (a !== b) { next[a].add(b); next[b].add(a); } }
  // ...and its PERIMETER, every edge where it ends (a crease to another face, or the mesh's own edge): with the area, how
  // WIDE it is (2 area / perimeter -- a long strip's width, a square's half side) -- a ledge, or a floor one can stand on
  const facePerim = new Float64Array(members.length), seen = new Map();
  for (let t = 0; t < T; t++) for (let e = 0; e < 3; e++) {
    const i = I[t * 3 + e], j = I[t * 3 + (e + 1) % 3], key = i < j ? i * nv + j : j * nv + i, o = seen.get(key);
    if (o === undefined) { seen.set(key, t); continue; }
    seen.set(key, -1);
    if (o >= 0 && comp[o] !== comp[t]) { const l = Math.hypot(P[i * 3] - P[j * 3], P[i * 3 + 1] - P[j * 3 + 1], P[i * 3 + 2] - P[j * 3 + 2]); facePerim[comp[o]] += l; facePerim[comp[t]] += l; }
  }
  for (const [key, t] of seen) if (t >= 0) { const i = Math.floor(key / nv), j = key % nv; facePerim[comp[t]] += Math.hypot(P[i * 3] - P[j * 3], P[i * 3 + 1] - P[j * 3 + 1], P[i * 3 + 2] - P[j * 3 + 2]); }
  const faceWidth = faceArea.map((A, c) => 2 * A / (facePerim[c] || 1));
  F = { comp, members, nrm, cen, area, ylo, yhi, P, I, faceArea, faceWidth, next: next.map((x) => [...x]) };
  faceCache.set(p, F);
  return F;
}

// a part's own measures, for mapping round it: its radius and (a dome) its meridian's length at every height
const partInfo = new WeakMap();
function infoOf(p) {
  let f = partInfo.get(p);
  if (f) return f;
  const P = p.geometry.position;
  let R = 0, y0 = Infinity;
  const rows = new Map();
  for (let i = 0; i < P.length; i += 3) {
    const r = Math.hypot(P[i], P[i + 2]); if (r > R) R = r; if (P[i + 1] < y0) y0 = P[i + 1];
    const k = Math.round(P[i + 1] * 100);
    if (!rows.has(k) || rows.get(k) < r) rows.set(k, r);
  }
  const mer = [...rows].sort((a, b) => a[0] - b[0]).map(([k, r]) => [k / 100, r]);
  const S = [0];
  for (let i = 1; i < mer.length; i++) S.push(S[i - 1] + Math.hypot(mer[i][0] - mer[i - 1][0], mer[i][1] - mer[i - 1][1]));
  const along = (y) => {                            // the meridian's length from the foot up to height y (local)
    if (mer.length < 2) return y;
    if (y <= mer[0][0]) return y - mer[0][0];
    for (let i = 1; i < mer.length; i++) if (y <= mer[i][0]) return S[i - 1] + (S[i] - S[i - 1]) * (y - mer[i - 1][0]) / (mer[i][0] - mer[i - 1][0]);
    return S[S.length - 1] + y - mer[mer.length - 1][0];
  };
  // a roof's slope: the mean sine of its upward faces' pitch (v up a roof is its height over that) -- of the faces
  // mapped up the slope, that is: a flat top is mapped on the plan, and a stepped roof's (a samvarana's courses) would
  // drag the mean down and squeeze its courses
  let sw = 0, ss = 0;
  const I = p.geometry.index;
  for (let k = 0; k < I.length; k += 3) {
    const a = I[k] * 3, b = I[k + 1] * 3, c = I[k + 2] * 3;
    const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx, l = Math.hypot(nx, ny, nz);
    if (l > 1e-12 && ny / l > .2 && ny / l <= .95) { sw += l; ss += l * Math.sqrt(Math.max(0, 1 - (ny / l) ** 2)); }
  }
  f = { R, y0, along, sinSlope: sw > 0 ? Math.max(.2, ss / sw) : 1 };
  partInfo.set(p, f);
  return f;
}

// THE PIECES: every triangle of the building (each copy of each part) cut where it must be, classified, matched and
// mapped. Returns { groups: [{ rule (null: the stone), glass, pos, nor, uv }], stats }. `sizeOf(rule)`: the rule's
// pattern's tile in metres (patterns.js); `seconds`: the budget classification may take before it is abandoned (the
// rest then counts as inside) -- a safeguard, not a setting.
// ---- ONE FACE WHERE TWO PARTS MEET IN A PLANE ------------------------------------------------------------------------
// Two parts whose faces lie in one plane, facing the same way, overlapping -- a floor's edge in a wall's face, a cornice
// in its drum's, two roofs over one corner, two fences' posts at one corner -- draw the same place twice, and the depth
// buffer flips between them (the flicker). So the place is KEPT BY ONE: of each pair of such triangles the larger keeps
// it (the wall's face, not the floor's 5 cm edge; on a tie the part that comes first), and the other has it CUT OUT.
// covers(): for each triangle that loses somewhere, the triangles it loses to -- in a 2D frame of their plane
function coverIndex(asm) {
  if (globalThis.location?.search?.includes("nocover")) return new Map();   // (?nocover: without it, to compare)
  const tris = [];   // { o (owner: part + copy), pi, k (triangle), n, d, A (area), q (3 pts) }
  asm.parts.forEach((p, pi) => {
    if (p.kind === "item" || p.kind === "glass" || p.kind === "marker" || !p.geometry?.index) return;
    const P = p.geometry.position, I = p.geometry.index;
    p.instances.forEach(([yaw, X, Y, Z], inst) => {
      const c = Math.cos(yaw), s = Math.sin(yaw), W = (j) => [P[j * 3] * c + P[j * 3 + 2] * s + X, P[j * 3 + 1] + Y, -P[j * 3] * s + P[j * 3 + 2] * c + Z];
      for (let k = 0; k < I.length; k += 3) {
        const a = W(I[k]), b = W(I[k + 1]), d = W(I[k + 2]);
        const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2], vx = d[0] - a[0], vy = d[1] - a[1], vz = d[2] - a[2];
        const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx, l = Math.hypot(nx, ny, nz);
        if (l < 1e-9) continue;
        const n = [nx / l, ny / l, nz / l];
        tris.push({ o: pi * 4096 + inst, pi, inst, k: k / 3, n, d: n[0] * a[0] + n[1] * a[1] + n[2] * a[2], A: l / 2, q: [a, b, d] });
      }
    });
  });
  const byN = new Map();
  for (const t of tris) { const key = t.n.map((v) => Math.round(v * 100)).join(","); (byN.get(key) ?? byN.set(key, []).get(key)).push(t); }
  const losers = new Map();   // "pi#inst#k" -> [{ ax, poly2 }]
  const axisOf = (n) => (Math.abs(n[0]) > Math.abs(n[1]) ? (Math.abs(n[0]) > Math.abs(n[2]) ? 0 : 2) : (Math.abs(n[1]) > Math.abs(n[2]) ? 1 : 2));
  const test = (A, B) => {
    if (A.o === B.o || Math.abs(A.d - B.d) > .002 || A.n[0] * B.n[0] + A.n[1] * B.n[1] + A.n[2] * B.n[2] < .9995) return;
    const ax = A.ax, qa = A.q2, qb = B.q2;
    if (!(A.b[0] < B.b[2] - 1e-5 && B.b[0] < A.b[2] - 1e-5 && A.b[1] < B.b[3] - 1e-5 && B.b[1] < A.b[3] - 1e-5)) return;
    {
        if (Math.abs(polyArea(clipConvex(qa, qb))) < 1e-5) return;
        // the larger keeps it; on a tie (within 1%) the part that comes first
        const [win, lose, qw] = B.A > A.A * 1.01 || (Math.abs(B.A - A.A) <= A.A * .01 && B.pi < A.pi) ? [B, A, qb] : [A, B, qa];
        const key = lose.pi + "#" + lose.inst + "#" + lose.k;
        (losers.get(key) ?? losers.set(key, []).get(key)).push({ ax, w: qw });
    }
  };
  for (const list of byN.values()) {
    if (list.length < 2) continue;
    list.sort((a, b) => a.d - b.d);
    // the plane's own clusters (d within 2mm of the one before), and in each the triangles met through a GRID of their
    // 2D boxes -- a large floor is thousands of triangles of one part in one plane, and all-against-all was minutes
    for (let i0 = 0; i0 < list.length;) {
      let i1 = i0 + 1;
      while (i1 < list.length && list[i1].d - list[i1 - 1].d < .002) i1++;
      const cl = list.slice(i0, i1); i0 = i1;
      if (cl.length < 2 || new Set(cl.map((t) => t.o)).size < 2) continue;
      // (one axis to draw the whole cluster on: a face at 45 degrees is as much x as z, and two of its triangles drawn on
      //  different axes would be compared in coordinates that are not the same -- two towers' faces on one diagonal met)
      const ax0 = axisOf(cl[0].n);
      for (const t of cl) {
        const ax = t.ax = ax0, f = (v) => (ax === 0 ? [v[1], v[2]] : ax === 1 ? [v[0], v[2]] : [v[0], v[1]]);
        t.q2 = ccw(t.q.map(f));
        const xs = t.q2.map((v) => v[0]), ys = t.q2.map((v) => v[1]);
        t.b = [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
      }
      if (cl.length <= 48) { for (let i = 0; i < cl.length; i++) for (let j = i + 1; j < cl.length; j++) test(cl[i], cl[j]); continue; }
      const C = Math.max(.5, Math.sqrt(cl.reduce((a, t) => a + (t.b[2] - t.b[0]) * (t.b[3] - t.b[1]), 0) / cl.length)), grid = new Map(), seen = new Set();
      cl.forEach((t, ti) => {
        for (let gx = Math.floor(t.b[0] / C); gx <= Math.floor(t.b[2] / C); gx++) for (let gy = Math.floor(t.b[1] / C); gy <= Math.floor(t.b[3] / C); gy++) {
          const key = gx * 100003 + gy, cell = grid.get(key);
          if (!cell) { grid.set(key, [ti]); continue; }
          for (const tj of cell) {
            if (cl[tj].o === t.o) continue;
            const pk = tj * 1e6 + ti;
            if (seen.has(pk)) continue;
            seen.add(pk); test(cl[tj], t);
          }
          cell.push(ti);
        }
      });
    }
  }
  return losers;
}
const polyArea = (q) => { let A = 0; for (let i = 0; i < q.length; i++) { const [x1, y1] = q[i], [x2, y2] = q[(i + 1) % q.length]; A += x1 * y2 - x2 * y1; } return A / 2; };
const ccw = (q) => (polyArea(q) < 0 ? q.slice().reverse() : q);
const boxesMeet = (a, b) => { const ax = a.map((v) => v[0]), ay = a.map((v) => v[1]), bx = b.map((v) => v[0]), by = b.map((v) => v[1]);
  return Math.min(...ax) < Math.max(...bx) - 1e-5 && Math.min(...bx) < Math.max(...ax) - 1e-5 && Math.min(...ay) < Math.max(...by) - 1e-5 && Math.min(...by) < Math.max(...ay) - 1e-5; };
function clipConvex(subj, clipP) {   // the part of `subj` inside the convex counter-clockwise `clipP` (Sutherland-Hodgman)
  let out = subj;
  for (let i = 0; i < clipP.length && out.length; i++) {
    const [ax, ay] = clipP[i], [bx, by] = clipP[(i + 1) % clipP.length], inp = out; out = [];
    const side = (v) => (bx - ax) * (v[1] - ay) - (by - ay) * (v[0] - ax);
    for (let j = 0; j < inp.length; j++) {
      const P = inp[j], Q = inp[(j + 1) % inp.length], sp = side(P), sq = side(Q);
      if (sp >= 0) out.push(P);
      if ((sp >= 0) !== (sq >= 0)) { const t = sp / (sp - sq); out.push(P.map((v, k) => v + (Q[k] - v) * t)); }
    }
  }
  return out;
}
// a convex polygon (3D, on its plane) less a convex cover: the pieces outside it, each convex -- cut by each of the
// cover's edges in turn (what lies outside an edge goes, what lies inside goes on to the next)
function minusCover(poly, ax, cover) {
  const f = (v) => (ax === 0 ? [v[1], v[2]] : ax === 1 ? [v[0], v[2]] : [v[0], v[1]]);
  const out = [];
  let rest = poly;
  for (let i = 0; i < cover.length && rest.length > 2; i++) {
    const [x0, y0] = cover[i], [x1, y1] = cover[(i + 1) % cover.length];
    const side = (v) => { const [x, y] = f(v); return (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0); };
    const inside = [], outside = [];
    for (let j = 0; j < rest.length; j++) {
      const P = rest[j], Q = rest[(j + 1) % rest.length], sp = side(P), sq = side(Q);
      if (sp >= 0) inside.push(P); if (sp <= 0) outside.push(P);
      if ((sp > 0 && sq < 0) || (sp < 0 && sq > 0)) { const t = sp / (sp - sq), m = P.map((v, k) => v + (Q[k] - v) * t); inside.push(m); outside.push(m); }
    }
    if (outside.length > 2 && Math.abs(polyArea(outside.map(f))) > 1e-7) out.push(outside);
    rest = inside;
  }
  return out;   // (what was left inside every edge is the covered part: dropped)
}

export function finishPieces(asm, finish, { sizeOf = () => [1, 1] } = {}) {
  const t0 = performance.now();
  const covered = coverIndex(asm);   // (where another part's face takes this one's place in a plane)
  const rules = (finish?.rules ?? []).map((r) => compile(r, sizeOf));
  const needSide = rules.some((r) => r.needsSide);
  const tell = needSide ? sideTeller(asm) : null;
  // the lines every piece is cut on: bands, regions
  const bands = [...new Set(rules.flatMap((r) => [r.rule.below, r.rule.above]).filter((v) => v !== undefined))].map((c) => [1, c]);
  const regions = rules.filter((r) => r.within).flatMap((r) => [[0, r.within[0]], [0, r.within[2]], [2, r.within[1]], [2, r.within[3]]]);
  const lines0 = [...bands, ...regions];
  const groups = new Map();
  // (what each wall FACE was given, by area: a face that comes out in two finishes is either cut on purpose -- a level
  //  line where it passes from inside to out -- or patchy, a stray piece of another finish in it: `mix`, for the checks)
  const mix = new Map();
  const groupOf = (key, rule, glass) => { let g = groups.get(key); if (!g) groups.set(key, g = { rule, glass, pos: [], nor: [], uv: rule?.pattern ? [] : null, parts: new Map() }); return g; };
  // THE PIECE BEING MATCHED, one record for all of them (no object per piece: a building is a hundred thousand of them):
  // its part and copy, normal and centre, and -- asked for only when a rule needs it -- its side and its surface
  const sideOf = () => {
    const { p, n, cen, X, Z, surf0, inst } = cur;
    if (!tell || cur.glass) return "out";
    // (a dome's or a round roof's face turned toward its own axis is its underside: inside)
    if ((p.kind === "dome" || p.kind === "vault") && n[1] < .3 && n[0] * (cen[0] - X) + n[2] * (cen[2] - Z) < 0) return "in";
    const sf = surf0 === "top" ? "floor" : surf0, roofy = ROOFY.has(p.kind);
    // a FLOOR is its face's too, asked at points spread over it -- unless they disagree on a floor that runs from a room
    // out onto a terrace (a building's platform, through its doorways): that is asked where it is, every 3m (it is cut
    // on a grid for this)
    if (surf0 === "floor") {
      const fs = floorSideOf(p, inst, facesOf(p).comp[cur.tri]);
      if (fs !== "mixed") return fs;
      // (a piece of a floor that is split -- inside and out -- is asked at a point of it with open air over it: the part
      //  of it that can be seen decides, not the part under a wall or a shell, which would paint teeth beside them)
      const poly = cur.poly, pts = [cen, ...poly.map((v) => [v[0] + (cen[0] - v[0]) * .15, v[1], v[2] + (cen[2] - v[2]) * .15])];
      for (const q of pts) if (!tell.hidden(q, UP, p.name, .5)) return tell(q, n, sf, roofy);
      return tell(cen, n, sf, roofy);
    }
    // anything else is inside or out by its FACE (facesOf: a wall's face, a dome's skin, a vault's soffit) and the band
    // of it this piece is in (bandsOf)
    const fb = cur.fb ?? bandsOf(p, inst, facesOf(p).comp[cur.tri]);
    // (the side of the stretch between the cuts it lies within)
    let i = 0; while (i < fb.cuts.length && cen[1] > fb.cuts[i]) i++;
    return fb.runs[i];
  };
  // A FACE IN BANDS. A face is inside or out as a whole unless part of it stands inside another part and part of it
  // outside -- a tower's face toward the church, inside below the church's roof and outside above it. So a face is asked
  // in level BANDS about 3m tall, each at points at its own mid-height on the face's largest triangles (the way most of
  // that area goes), and it is cut where two bands disagree: the finish changes on a level line across the element,
  // never along a triangle's edge.
  const floorSides = new Map();
  const floorSideOf = (p, inst, comp) => {
    const key = p.name + "#" + inst + "#" + comp;
    let v = floorSides.get(key);
    if (v) return v;
    const F = facesOf(p), [yaw, X, Y, Z] = p.instances[inst], c = Math.cos(yaw), s2 = Math.sin(yaw);
    const W = (x, y, z) => [x * c + z * s2 + X, y + Y, -x * s2 + z * c + Z];
    // (points: its largest triangles' centres, and halfway to the corners of the large ones; eight of them, each as far
    //  as it can be from those already taken)
    const pts = [];
    for (const t of F.members[comp].slice(0, 16)) {
      const cx = F.cen[t * 3], cy = F.cen[t * 3 + 1], cz = F.cen[t * 3 + 2];
      pts.push(W(cx, cy, cz));
      if (F.area[t] > 20) for (let e = 0; e < 3; e++) { const i = F.I[t * 3 + e] * 3; pts.push(W((cx + F.P[i]) / 2, cy, (cz + F.P[i + 2]) / 2)); }
    }
    const pick = [pts[0]];
    while (pick.length < Math.min(8, pts.length)) {
      let best = null, bd = -1;
      for (const q of pts) { const d = Math.min(...pick.map((r) => Math.hypot(q[0] - r[0], q[2] - r[2]))); if (d > bd) { bd = d; best = q; } }
      if (bd < .5) break;
      pick.push(best);
    }
    // (only where there is open air over it: a point under a wall or a column's shaft sees nothing -- and a floor with
    //  no such point is hidden, and may as well be outside)
    const open = pick.filter((q) => !tell.hidden(q, UP, p.name, .5));
    if (!open.length) { floorSides.set(key, "out"); return "out"; }
    const n = [0, 1, 0], said = open.map((q) => tell(q, n, "floor", ROOFY.has(p.kind))), outs = said.filter((x) => x === "out").length;
    // (unanimous: that. Split: only a building's platform or a floor too large to be one room is cut and asked where it
    //  is -- it runs from the nave out before the door; any other floor -- a drum's top, a colonnade's walk, a terrace, a
    //  landing -- is one element, and goes the way most of it goes)
    v = outs === said.length ? "out" : outs === 0 ? "in" : p.kind === "base" || F.faceArea[comp] > 400 ? "mixed" : outs * 2 >= said.length ? "out" : "in";
    floorSides.set(key, v);
    return v;
  };
  // (a piece of a split floor whose points with open air over them disagree is HALVED, and its halves asked again, down
  //  to half a metre: the finish follows a wall's foot and a portal's jambs, not the 2m grid it was cut on)
  const refine = (p, poly) => {
    let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity, cx = 0, cy = 0, cz = 0;
    for (const v of poly) { x0 = Math.min(x0, v[0]); x1 = Math.max(x1, v[0]); z0 = Math.min(z0, v[2]); z1 = Math.max(z1, v[2]); cx += v[0]; cy += v[1]; cz += v[2]; }
    if (Math.max(x1 - x0, z1 - z0) <= .6) return [poly];
    const cen = [cx / poly.length, cy / poly.length, cz / poly.length];
    const pts = [cen, ...poly.map((v) => [v[0] + (cen[0] - v[0]) * .15, v[1], v[2] + (cen[2] - v[2]) * .15])];
    const open = pts.filter((q) => !tell.hidden(q, UP, p.name, .5)), said = new Set(open.map((q) => tell(q, UP, "floor")));
    // (and one a wall's foot crosses -- some of its points under stone, some open -- is halved too, even if the open
    //  ones agree: the sliver of it past the wall's other face, between its points, may be the other side's)
    if (said.size < 2 && (open.length === pts.length || !open.length)) return [poly];
    return cutAll(poly, [x1 - x0 >= z1 - z0 ? [0, (x0 + x1) / 2] : [2, (z0 + z1) / 2]]).flatMap((q) => refine(p, q));
  };
  const faceBands = new Map();
  const bandsOf = (p, inst, comp) => {
    const key = p.name + "#" + inst + "#" + comp;
    let b = faceBands.get(key);
    if (b) return b;
    const F = facesOf(p), tris = F.members[comp], [yaw, X, Y, Z] = p.instances[inst], c = Math.cos(yaw), s2 = Math.sin(yaw);
    const W = (x, y, z) => [x * c + z * s2 + X, y + Y, -x * s2 + z * c + Z], Wn = (x, y, z) => [x * c + z * s2, y, -x * s2 + z * c];
    let y0 = Infinity, y1 = -Infinity;
    for (const t of tris) { if (F.ylo[t] < y0) y0 = F.ylo[t]; if (F.yhi[t] > y1) y1 = F.yhi[t]; }
    const nb = Math.max(1, Math.round((y1 - y0) / 3)), h = Math.max(1e-6, (y1 - y0) / nb), sides = [];
    // (the face asked at one height: in, out, or null where nothing of it crosses that level)
    const ask = (ym) => {
      let wIn = 0, wOut = 0, used = 0;
      // (where it is asked: at points spread EVENLY ALONG the face at this height -- the line the level cuts through it --
      //  each counting alike: so a drum or a column's shaft is asked all round, and a facade along its length, not at
      //  its largest triangles, which may be its two ends buried in the hollow towers flanking it; a tie is outside)
      // (and only where the face is open in front: a point behind a column or a pier standing against it, or buried in
      //  one standing half into it, is hidden, and would call a facade inside -- passed over for the next point along)
      const segs = [];
      let L = 0;
      for (const t of tris) {
        if (F.ylo[t] > ym + 1e-6 || F.yhi[t] < ym - 1e-6) continue;
        const q = [0, 1, 2].map((e) => { const i = F.I[t * 3 + e] * 3; return [F.P[i], F.P[i + 1], F.P[i + 2]]; }), hit = [];
        for (let e = 0; e < 3; e++) {
          const u = q[e], d = q[(e + 1) % 3];
          if ((u[1] - ym) * (d[1] - ym) <= 0 && u[1] !== d[1]) { const f = (ym - u[1]) / (d[1] - u[1]); hit.push([u[0] + (d[0] - u[0]) * f, ym, u[2] + (d[2] - u[2]) * f]); }
        }
        // (a level triangle -- a face lying at this very height -- is a point at its centre, as long as it is wide)
        const c = [F.cen[t * 3], F.cen[t * 3 + 1], F.cen[t * 3 + 2]];
        const [u, d, len] = hit.length < 2 ? [c, c, Math.sqrt(F.area[t])] : [hit[0], hit[1], Math.hypot(hit[1][0] - hit[0][0], hit[1][2] - hit[0][2])];
        if (len < 1e-6) continue;
        segs.push([t, u, d, L, len]); L += len;
      }
      const SAMPLES = 5, TRIES = SAMPLES * 2, picks = [];
      // (ten places along it, the even ones first: if some are hidden the odd ones between stand in)
      for (const i of [...Array(TRIES).keys()].sort((x, y) => (x & 1) - (y & 1) || x - y)) {
        if (picks.length >= SAMPLES || !segs.length) break;
        const at = (i + .5) / TRIES * L;
        let lo = 0, hi = segs.length - 1;
        while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (segs[mid][3] <= at) lo = mid; else hi = mid - 1; }
        const [t, u, d, s0, len] = segs[lo], f = Math.min(1, Math.max(0, (at - s0) / len));
        const q = W(u[0] + (d[0] - u[0]) * f, ym, u[2] + (d[2] - u[2]) * f), n = Wn(F.nrm[t * 3], F.nrm[t * 3 + 1], F.nrm[t * 3 + 2]);
        if (tell.hidden(q, n, p.name, .6)) continue;
        picks.push([t, q, n]);
      }
      for (const [t, cen, n] of picks) {
        // (a dome's or a round roof's face turned toward its own axis is its underside: inside, without a ray)
        const inward = (p.kind === "dome" || p.kind === "vault") && n[1] < .3 && n[0] * (cen[0] - X) + n[2] * (cen[2] - Z) < 0;
        const sf = n[1] >= .7 ? "floor" : n[1] <= -.7 ? "ceiling" : "wall";
        if (inward || tell(cen, n, sf, ROOFY.has(p.kind)) === "in") wIn++; else wOut++;
        used++;
      }
      // (a face that wraps round -- samples facing opposite ways: a column, a drum -- is outside if a quarter of it looks
      //  out onto open air: a colonnade's column, whose inner side faces its drum a metre away; a column in a hall sees
      //  nothing anywhere. A flat face goes the way most of it goes.)
      let wraps = false;
      for (const [, , a] of picks) for (const [, , b] of picks) if (a[0] * b[0] + a[1] * b[1] + a[2] * b[2] < 0) wraps = true;
      return used ? ((wraps ? wOut >= .25 * (wIn + wOut) : wOut >= wIn) ? "out" : "in") : null;
    };
    for (let k = 0; k < nb; k++) sides.push(ask(y0 + (k + .5) * h));
    const asked = sides.slice();
    // (a band no triangle crosses at its middle -- a gap in the face -- goes as its neighbour does)
    for (let k = 0; k < nb; k++) if (!sides[k]) sides[k] = sides.slice(0, k).reverse().find(Boolean) ?? sides.slice(k).find(Boolean) ?? "out";
    // A REVEAL IS ITS WALL'S: the jamb, sill or soffit of an opening looks across the opening into the other jamb and up
    // into the lintel, and measures as closed in -- but it is the masonry of the wall it pierces. So a face found inside
    // takes the side of any larger face it meets along a crease, at its own height, if that one is outside: an outside
    // window's reveals follow the facade, and an opening between two rooms stays inside. (Larger only: it cannot go round.)
    for (let k = 0; k < nb; k++) {
      if (sides[k] !== "in") continue;
      const ym = y0 + (k + .5) * h + Y;
      for (const o of F.next[comp]) {
        if (F.faceArea[o] <= F.faceArea[comp] * 1.2) continue;
        const ob = bandsOf(p, inst, o);
        if (ob.sides[Math.max(0, Math.min(ob.sides.length - 1, Math.floor((ym - ob.y0) / ob.h)))] === "out") { sides[k] = "out"; break; }
      }
    }
    // WHERE IT CHANGES: between two bands that disagree the face is asked again, halving the gap down to 20cm -- so the
    // finish changes where the roof that closes it in meets it, not on the 3m grid it was asked on (two bands as asked;
    // one a reveal took over goes on the grid line)
    const cuts = [];
    for (let k = 1; k < nb; k++) {
      if (sides[k] === sides[k - 1]) continue;
      let lo = y0 + (k - .5) * h, hi = y0 + (k + .5) * h;
      if (asked[k - 1] === sides[k - 1] && asked[k] === sides[k]) {
        while (hi - lo > .2) { const mid = (lo + hi) / 2, a = ask(mid); if (a === sides[k - 1]) lo = mid; else if (a === sides[k]) hi = mid; else break; }
        if (hi - lo > .2) { lo = hi = y0 + k * h; }
      } else lo = hi = y0 + k * h;
      cuts.push(Y + (lo + hi) / 2);
    }
    const runs = [sides[0]];
    for (let k = 1; k < nb; k++) if (sides[k] !== sides[k - 1]) runs.push(sides[k]);
    faceBands.set(key, b = { y0: y0 + Y, h, sides, cuts, runs });
    return b;
  };
  const cur = {
    p: null, names: null, glass: false, inst: 0, yaw: 0, X: 0, Z: 0, n: null, cen: null, poly: null, tri: 0, fb: null, surf0: "", sideV: null, surfV: null,
    side: () => cur.sideV ??= sideOf(),
    // (a roof's GABLE -- the vertical end of a gable roof, a verge -- is a wall: it takes the finish of the walls under it)
    surface: () => cur.surfV ??= (ROOFY.has(cur.p.kind) && cur.n[1] > -.2 && !(cur.p.kind === "roof" && Math.abs(cur.n[1]) < .05) ? (cur.side() === "out" ? "roof" : "wall")
                                  : cur.surf0 === "top" ? (cur.side() === "out" ? "roof" : "wall") : cur.surf0),
  };
  for (const [pi, p] of asm.parts.entries()) {
    if (p.kind === "item") continue;   // (a piece of furniture: its box is the walk's, the item draws itself -- architecture.js itemMeshes)
    const P = p.geometry.position, I = p.geometry.index, names = partNames(p), glass = p.kind === "glass";
    const mine = rules.filter((r) => r.mayMatch(names));            // (the rules this part can meet at all)
    const sideRules = !!tell && mine.some((r) => r.needsSide);
    const info = infoOf(p);
    cur.p = p; cur.names = names; cur.glass = glass;
    for (const [inst, [yaw, X, Y, Z]] of p.instances.entries()) {
      cur.inst = inst; cur.yaw = yaw; cur.X = X; cur.Z = Z;
      const c = Math.cos(yaw), s = Math.sin(yaw);
      const W = (j) => [P[j * 3] * c + P[j * 3 + 2] * s + X, P[j * 3 + 1] + Y, -P[j * 3] * s + P[j * 3 + 2] * c + Z];
      for (let k = 0; k < I.length; k += 3) {
        const a = W(I[k]), b = W(I[k + 1]), d = W(I[k + 2]);
        const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2], vx = d[0] - a[0], vy = d[1] - a[1], vz = d[2] - a[2];
        const nx0 = uy * vz - uz * vy, ny0 = uz * vx - ux * vz, nz0 = ux * vy - uy * vx, area2 = Math.hypot(nx0, ny0, nz0);
        if (area2 < 1e-12) continue;
        const n = [nx0 / area2, ny0 / area2, nz0 / area2];
        cur.n = n; cur.tri = k / 3;
        let surf0 = TRIM.has(p.kind) ? "wall" : n[1] >= .7 ? (FLOORLESS.has(p.kind) ? "top" : "floor") : n[1] <= -.7 ? "ceiling" : "wall";
        // (a LEDGE -- a sill, a cornice's top, a column base's ring round its shaft, a merlon's top, a buttress's set-off
        //  or its head -- faces up but is no floor: a column's, or anything under 2 square metres or too narrow to stand
        //  on (under 90cm wide) that is not a stair's tread, is the masonry of its element, like its walls; and so is
        //  every up-facing face of a wall -- its sills, its set-backs, its top -- unless the wall is walked)
        if (surf0 === "floor" && !STAIRS.has(p.kind) && !p.walked) {
          const F = facesOf(p), c = F.comp[k / 3];
          if (p.kind === "column" || p.kind === "wall" || F.faceArea[c] < 2 || F.faceWidth[c] < .9) surf0 = "wall";
        }
        cur.surf0 = surf0;
        // (large floors are cut on a 2m grid, so a platform under a church and before its door is inside and out)
        let lines = lines0;
        if (surf0 === "floor" && area2 > 8) {
          lines = lines0.slice();
          const xs = [a[0], b[0], d[0]], zs = [a[2], b[2], d[2]];
          for (let x = Math.ceil(Math.min(...xs) / 2) * 2; x < Math.max(...xs); x += 2) lines.push([0, x]);
          for (let z = Math.ceil(Math.min(...zs) / 2) * 2; z < Math.max(...zs); z += 2) lines.push([2, z]);
        }
        cur.fb = null;
        if (sideRules && !glass && surf0 !== "floor" && !TRIM.has(p.kind) && !p.side) {
          const fb = cur.fb = bandsOf(p, inst, facesOf(p).comp[k / 3]);
          if (fb.cuts.length) {
            const lo = Math.min(a[1], b[1], d[1]), hi = Math.max(a[1], b[1], d[1]);
            const own = fb.cuts.filter((y) => y > lo + 1e-6 && y < hi - 1e-6);
            if (own.length) lines = [...lines, ...own.map((y) => [1, y])];
          }
        }
        let polys = lines.length ? cutAll([a, b, d], lines) : [[a, b, d]];
        const cov = covered.get(pi + "#" + inst + "#" + k / 3);
        if (cov) for (const { ax, w } of cov) polys = polys.flatMap((q) => minusCover(q, ax, w));   // (one face where two parts meet in a plane)
        if (!polys.length) continue;
        if (surf0 === "floor" && tell && floorSideOf(p, inst, facesOf(p).comp[k / 3]) === "mixed") polys = polys.flatMap((q) => refine(p, q));
        for (const poly of polys) {
          let cx = 0, cy = 0, cz = 0;
          for (const v of poly) { cx += v[0]; cy += v[1]; cz += v[2]; }
          const cen = [cx / poly.length, cy / poly.length, cz / poly.length];
          cur.cen = cen; cur.poly = poly; cur.sideV = p.side ?? (TRIM.has(p.kind) ? "out" : null); cur.surfV = null;
          let hit = mine.find((r) => r.test(cur));
          // (a soffit -- under an arch, a window's head -- that no rule takes is the masonry of its wall)
          if (!hit && cur.surface() === "ceiling") { cur.surfV = "wall"; hit = mine.find((r) => r.test(cur)); }
          const g = hit ? groupOf(rules.indexOf(hit), hit.rule, glass) : groupOf(glass ? "glass" : "stone", null, glass);
          g.parts.set(p.name, (g.parts.get(p.name) ?? 0) + 1);             // (what each rule took, for the viewer and the checks)
          if (!glass && !TRIM.has(p.kind) && p.kind !== "dome" && p.kind !== "vault" && cur.surface() === "wall") {
            let ar = 0;
            for (let i = 1; i + 1 < poly.length; i++) {
              const A = poly[0], B = poly[i], C = poly[i + 1], u = [B[0] - A[0], B[1] - A[1], B[2] - A[2]], v = [C[0] - A[0], C[1] - A[1], C[2] - A[2]];
              ar += Math.hypot(u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]) / 2;
            }
            // (keyed by its FACE -- facesOf: all of a plane that touches, the pieces an opening or a tier's seam cut
            //  apart one face)
            const fk = pi + "#" + inst + "#" + facesOf(p).comp[k / 3], gk = hit ? rules.indexOf(hit) : "stone";
            // (and in which CELL of it: between which of the rules' lines and the face's own level cuts its centre lies --
            //  one cell, one finish; two in one cell are a patch, not a band)
            const cell = lines0.map(([ax, c]) => +(cen[ax] > c)).join("") + "/" + Math.max(-1, ...(cur.fb?.cuts ?? []).filter((y) => cen[1] > y)).toFixed(2);
            let fm = mix.get(fk); if (!fm) mix.set(fk, fm = { by: new Map(), cells: new Map(), at: new Map() });
            fm.by.set(gk, (fm.by.get(gk) ?? 0) + ar);
            if (!fm.at.has(gk)) fm.at.set(gk, cen.map((q) => +q.toFixed(2)));   // (where each finish was first met: for the checks' report)
            let cm = fm.cells.get(cell); if (!cm) fm.cells.set(cell, cm = new Map());
            cm.set(gk, (cm.get(gk) ?? 0) + ar);
          }
          // the pattern's coordinates, in metres
          let uvs = null;
          if (g.uv) {
            const r = hit.rule, size = hit.size ??= sizeOf(r).map((q) => q * (r.scale ?? 1));   // (worked out once a rule)
            let mode = r.map ?? (hit.panel ? "plan" : ["dome", "vault"].includes(p.kind) || (["column", "ring"].includes(p.kind) && Math.abs(n[1]) < .7) ? "revolve"
                                 : p.kind === "roof" ? "slope" : surf0 === "floor" || surf0 === "ceiling" ? "plan" : "face");
            if ((mode === "face" || mode === "slope") && Math.abs(n[1]) > .95) mode = "plan";
            if (mode === "slope" && Math.abs(n[1]) < .05) mode = "face";   // (a gable: its wall's own coordinates)
            const th = Math.hypot(n[0], n[2]) || 1, tx = n[2] / th, tz = -n[0] / th;
            if (mode === "revolve") {
              // (a whole number of tiles round -- `count` of them if the rule says: one carved panel to a balustrade's bay)
              const R = r.radius ?? info.R, C = (r.count ?? Math.max(1, Math.round(TAU * R / size[0]))) * size[0];
              let ang = poly.map((v) => Math.hypot(v[0] - X, v[2] - Z) < 1e-6 ? null : Math.atan2(v[0] - X, v[2] - Z));
              const known = ang.filter((q) => q !== null);
              if (known.length && Math.max(...known) - Math.min(...known) > Math.PI) ang = ang.map((q) => (q !== null && q < 0 ? q + TAU : q));
              const mean = known.length ? ang.filter((q) => q !== null).reduce((x, y) => x + y, 0) / known.length : 0;
              uvs = poly.map((v, i) => [(ang[i] ?? mean) / TAU * C, ["dome", "vault"].includes(p.kind) ? info.along(v[1] - Y) : v[1]]);
            } else if (mode === "plan") uvs = poly.map((v) => [v[0], -v[2]]);
            else if (mode === "slope") uvs = poly.map((v) => [v[0] * tx + v[2] * tz, v[1] / info.sinSlope]);
            else uvs = poly.map((v) => [v[0] * tx + v[2] * tz, v[1]]);
            if (hit.panel) uvs = uvs.map(([u, v]) => [u - hit.panel.cx, v + hit.panel.cz]);
            if (r.turn) { const cs = Math.cos(r.turn * Math.PI / 180), sn = Math.sin(r.turn * Math.PI / 180); uvs = uvs.map(([u, v]) => [u * cs - v * sn, u * sn + v * cs]); }
            if (r.align === "part") { const foot = info.y0 + Y; uvs = uvs.map(([u, v]) => [u, v - foot - size[1] / 2]); }
            if (r.offset) uvs = uvs.map(([u, v]) => [u + r.offset[0], v + r.offset[1]]);
          }
          for (let i = 1; i + 1 < poly.length; i++) for (const j of [0, i, i + 1]) {
            const v = poly[j];
            g.pos.push(v[0], v[1], v[2]); g.nor.push(n[0], n[1], n[2]);
            if (uvs) g.uv.push(uvs[j][0], uvs[j][1]);
          }
        }
      }
    }
  }
  const out = [...groups.values()].map((g) => ({ ...g, pos: new Float32Array(g.pos), nor: new Float32Array(g.nor), uv: g.uv ? new Float32Array(g.uv) : null }));
  // (the faces in more than one finish, each with its finishes' areas and how much of it is a PATCH: in a cell of it --
  //  between the rules' bands and regions and its own level cuts -- that another finish holds most of)
  const mixed = [...mix.entries()].filter(([, f]) => f.by.size > 1).map(([key, f]) => {
    const [pi, inst] = key.split("#").map(Number), total = [...f.by.values()].reduce((a, b) => a + b, 0);
    let patch = 0;
    for (const cm of f.cells.values()) { const v = [...cm.values()]; patch += v.reduce((a, b) => a + b, 0) - Math.max(...v); }
    return { part: asm.parts[pi].name, inst, total: +total.toFixed(2), minor: +(patch / total).toFixed(3), cuts: patch / total < 1e-3,
             by: Object.fromEntries([...f.by.entries()].map(([k, a]) => [k === "stone" ? "stone" : (rules[k].rule.pattern ?? rules[k].rule.color ?? k), +a.toFixed(2)])),
             at: Object.fromEntries([...f.at.entries()].map(([k, c]) => [k === "stone" ? "stone" : (rules[k].rule.pattern ?? rules[k].rule.color ?? k), c])) };
  });
  return { groups: out, mixed, stats: { ms: performance.now() - t0, ...(tell ? tell.stats() : {}) } };
}

// the params a rule's pattern is drawn with: its own, and a fitted panel's size (W, H) -- the one place both the tile's
// size and its texture are worked out from
export const ruleParams = (r) => ({ ...(r.params ?? {}), ...(r.fit ? { W: r.fit[2] - r.fit[0], H: r.fit[3] - r.fit[1] } : {}) });
// every pattern family the finish's rules name (to fetch before building)
export const familiesOf = (finish) => [...new Set((finish?.rules ?? []).filter((r) => r.pattern).map((r) => r.pattern.split("/")[0]))];
