// THE ARCHITECTURE ENGINE: definitions in, triangles out, and every piece meeting its neighbour EXACTLY.
//
// "Exactly" is the whole point of this engine, so it is worth saying what it means and how it is got:
//   * two pieces that touch share the same vertices -- the same numbers, not numbers within a tolerance;
//   * no T-junctions: an edge is never cut by a vertex that its neighbour does not also have (that is what
//     opens the hairline cracks you see in most procedural architecture);
//   * no overlaps: nothing is drawn twice in the same place, so nothing z-fights.
// Three things buy it. A WELD table, so a vertex asked for twice is the same index. A common CUT GRID: before
// a wall face is triangulated, every vertical strip is subdivided at the same set of heights, so a pier's
// edge and the arch band beside it break at the same points. And an ARCH CURVE that is generated once and
// shared by everything that touches it (profiles.js), with its springing points pinned to the exact numbers.
//
// The layers, lowest first: profiles (the curve an opening's head follows) -> openings -> a WALL FACE (a
// rectangle cut by openings, triangulated) -> extrusion, straight or RADIAL (a bay of a round building, whose
// side faces lie on the radial planes so its neighbours meet it exactly) -> parts -> a building.
import { archCurve, archRise } from "./profiles.js";
import { traceryMesh } from "./tracery.js";
import { wimpergMesh } from "./wimperg.js";
import { surroundMesh } from "./surround.js";
import { lombardMesh } from "./lombard.js";

const Q = 1e6;   // the weld grid: a micrometre. Two points that round to the same micrometre ARE the same point.

export function mesh() {
  const pos = [], idx = [], seen = new Map();
  const key = (x, y, z) => `${Math.round(x * Q)},${Math.round(y * Q)},${Math.round(z * Q)}`;
  const api = {
    vert(x, y, z) {
      const k = key(x, y, z);
      let i = seen.get(k);
      if (i === undefined) { i = pos.length / 3; pos.push(x, y, z); seen.set(k, i); }
      return i;
    },
    tri(a, b, c) { if (a !== b && b !== c && a !== c) idx.push(a, b, c); },
    quad(a, b, c, d) { api.tri(a, b, c); api.tri(a, c, d); },
    get counts() { return { verts: pos.length / 3, tris: idx.length / 3 }; },
    arrays() {
      return { position: new Float32Array(pos), index: (pos.length / 3 > 65535 ? Uint32Array : Uint16Array).from(idx) };
    },
  };
  return api;
}

// ---- the wall face -----------------------------------------------------------------------------------------
// A rectangle w x h, cut by openings. Each opening is { at, width, sill, head } where `head` is a profile
// definition (profiles.js) and `at` is the centre. The face is returned as a grid of points with the triangles
// of the SOLID parts and the loops that bound the holes -- the extruder needs the loops to build the reveals.
//
// The cut grid: x is cut at every opening's jambs, y at every sill and springing and at the top. Every strip
// is cut at every y, so a pier's right edge and the arch band's left edge break in the same places.
// EAR CLIPPING: a simple polygon into triangles, adding no points. The masonry over an arch is the one shape
// here that is neither a quad nor a fan -- it is bounded below by a curve that bulges INTO it (a semicircular
// head, or a horseshoe that comes back under itself) -- and triangulating it from a single point is only valid
// when every corner of it is in plain sight from that point, which for a round head it is not. Ear clipping is
// valid for any simple polygon, and it puts no vertex on the top edge, which is what the fans were for: the
// top edge, extruded, is a FLOOR (a vault's extrados, the top of an arcade wall) and must not be cut once per
// curve segment or every floor in the building multiplies with the arches' detail.
export function earClip(pts, loop) {
  const area2 = (l) => { let s = 0; for (let i = 0; i < l.length; i++) { const [x0, y0] = pts[l[i]], [x1, y1] = pts[l[(i + 1) % l.length]]; s += x0 * y1 - x1 * y0; } return s; };
  const v = area2(loop) < 0 ? loop.slice().reverse() : loop.slice();     // counter-clockwise
  const cross = (a, b, c) => (pts[b][0] - pts[a][0]) * (pts[c][1] - pts[a][1]) - (pts[b][1] - pts[a][1]) * (pts[c][0] - pts[a][0]);
  const inside = (a, b, c, p) => {
    const d1 = cross(a, b, p), d2 = cross(b, c, p), d3 = cross(c, a, p);
    return d1 >= -1e-12 && d2 >= -1e-12 && d3 >= -1e-12;
  };
  const out = [];
  let guard = v.length * v.length + 16;
  while (v.length > 3 && guard-- > 0) {
    let cut = false;
    for (let i = 0; i < v.length; i++) {
      const a = v[(i + v.length - 1) % v.length], b = v[i], c = v[(i + 1) % v.length];
      if (cross(a, b, c) <= 1e-12) continue;                              // reflex (or straight): not an ear
      let ok = true;
      for (const p of v) { if (p === a || p === b || p === c) continue; if (inside(a, b, c, p)) { ok = false; break; } }
      if (!ok) continue;
      out.push([a, b, c]);
      v.splice(i, 1);
      cut = true;
      break;
    }
    if (!cut) break;                                                      // (degenerate: take what there is)
  }
  if (v.length === 3) out.push([v[0], v[1], v[2]]);
  return out;
}

// `topCuts` / `bottomCuts`: x positions the top and bottom edges must carry a vertex at, besides their own --
// where this face stands on (or under) another face whose edge is broken there, so the two are one edge.
// `endCuts`: heights its two END verticals must carry -- where the next face round a corner is broken there.
export function wallFace(w, h, openings = [], { topCuts = [], bottomCuts = [], endCuts = [] } = {}) {
  const along = (list, a, b) => list.filter((x) => x > Math.min(a, b) + 1e-9 && x < Math.max(a, b) - 1e-9).sort((p, q) => (b > a ? p - q : q - p));
  // An opening is three heights, not one: the SILL it starts at, the SPRINGING where its head begins (the top
  // of the straight jambs), and the CROWN the head reaches. An arcade is mostly jamb -- a Roman arena's arch
  // springs at about half its height -- so a head sitting straight on the sill is not an arch, it is a hole.
  const ops = openings.map((o) => {
    const a = o.width / 2, sill = o.sill ?? 0, springing = o.springing ?? sill;
    if (springing < sill - 1e-9) throw new Error("an opening's springing line is below its sill");
    const curve = archCurve(a, o.head ?? {});
    // A HEAD MAY OVERHANG ITS OWN JAMBS: a horseshoe comes back in under itself, so the opening is wider above
    // the springing than the straight sides are. The jambs stay where they are (`j0`, `j1`) and the opening's
    // SPAN grows to whatever the curve reaches, with the shoulder between them left solid below the springing.
    let cx0 = -a, cx1 = a;
    for (const [cx] of curve) { if (cx < cx0) cx0 = cx; if (cx > cx1) cx1 = cx; }
    // (a millimetre clear of the bulge, so the shoulder beside it is a sliver and not a PINCH POINT, where the
    //  curve would touch the span's own edge and the masonry above would be a polygon touching itself)
    const grow = 1e-3;
    // A FOOT: a second profile below the sill, drawn downward -- so a round window (an oculus, a rose) is a
    // semicircular head over a semicircular foot with no jambs between, and a quatrefoil is two trefoils.
    const foot = o.foot ? archCurve(a, o.foot).map(([fx, fy]) => [fx, -fy]) : null;
    const dip = foot ? Math.max(...foot.map(([, fy]) => -fy)) : 0;
    if (foot && sill - dip < 1e-6) throw new Error(`an opening's foot reaches below the wall (${(sill - dip).toFixed(2)})`);
    return { ...o, a, sill, springing, j0: o.at - a, j1: o.at + a, foot,
             x0: o.at + (cx0 < -a - 1e-9 ? cx0 - grow : -a), x1: o.at + (cx1 > a + 1e-9 ? cx1 + grow : a),
             curve, crown: springing + archRise(a, o.head ?? {}) };
  }).sort((p, q) => p.x0 - q.x0);
  for (let i = 1; i < ops.length; i++) {
    if (ops[i].x0 < ops[i - 1].x1 - 1e-9) throw new Error("openings overlap");
  }
  for (const o of ops) {
    if (o.x0 < -1e-9 || o.x1 > w + 1e-9) throw new Error("an opening runs past the end of the wall");
    if (o.crown > h + 1e-9) throw new Error(`an opening's crown (${o.crown.toFixed(2)}) is above the wall (${h})`);
  }
  // WHICH HEIGHTS A VERTICAL IS BROKEN AT, and where. A cut exists for ONE reason: an edge that stands against
  // a neighbour's must be broken wherever the neighbour's is, or the two meet as one long edge against several
  // short ones -- a T-junction, a hairline crack on screen and an open edge in the mesh. So a cut belongs to
  // the OPENING that needs it, and reaches only the verticals beside that opening. A solid stretch of wall
  // between two openings carries their cuts on the sides that touch them and nothing in between; a wall with
  // no openings at all is one quad, whatever its height.
  //   (It used to be one grid over the whole face: every solid strip was cut at every opening's sill,
  // springing and crown, wherever they were, which is three or four quads of masonry where one would do.)
  const inner = (v) => v > 1e-9 && v < h - 1e-9;
  const ownCuts = (o) => [...new Set([o.sill, o.springing, o.crown].filter(inner))].sort((p, q) => p - q);
  const cutsAtX = (x) => {
    const set = new Set();
    for (const o of ops) if (Math.abs(o.x0 - x) < 1e-9 || Math.abs(o.x1 - x) < 1e-9) for (const v of ownCuts(o)) set.add(v);
    if (x < 1e-9 || x > w - 1e-9) for (const v of endCuts) if (v > 1e-9 && v < h - 1e-9) set.add(v);
    return [...set].sort((p, q) => p - q);
  };
  const ys = new Set([0, h]);
  for (const o of ops) { ys.add(o.sill); ys.add(o.springing); ys.add(o.crown); }
  const yCuts = [...ys].sort((a, b) => a - b);

  const pts = [], seen = new Map();
  const P = (x, y) => {
    const k = `${Math.round(x * Q)},${Math.round(y * Q)}`;
    let i = seen.get(k);
    if (i === undefined) { i = pts.length; pts.push([x, y]); seen.set(k, i); }
    return i;
  };
  const tris = [], holes = [];
  const quad = (a, b, c, d) => { tris.push([a, b, c], [a, c, d]); };
  // a solid strip from x0 to x1, over the full height: ONE polygon, with a vertex on each side only where the
  // opening beside it is broken. Ear-clipped, so the inside is the fewest triangles that polygon can be.
  const solid = (x0, x1) => {
    const L = cutsAtX(x0), R = cutsAtX(x1);
    const poly = [P(x0, 0), ...along(bottomCuts, x0, x1).map((c) => P(c, 0)), P(x1, 0), ...R.map((v) => P(x1, v)), P(x1, h),
                  ...along(topCuts, x1, x0).map((c) => P(c, h)), P(x0, h), ...L.slice().reverse().map((v) => P(x0, v))];
    tris.push(...earClip(pts, poly));
  };
  let x = 0;
  for (const o of ops) {
    if (o.x0 > x + 1e-9) solid(x, o.x0);
    // under the sill, if it has one: a solid block, broken where the walls beside it are
    const band = [0, ...ownCuts(o), h];
    if (o.foot && o.sill > 1e-9) {
      // the block under a FOOT: its top edge is the foot's curve, dipping into it -- one polygon, ear-clipped
      const f = o.foot.map(([fx, fy]) => P(o.at + fx, o.sill + fy));
      const poly = [P(o.x0, 0), ...along(bottomCuts, o.x0, o.x1).map((c) => P(c, 0)), P(o.x1, 0), P(o.x1, o.sill),
                    ...f.slice(0, -1).reverse().slice(0, -1), P(o.x0, o.sill)];
      const clean = poly.filter((v, i) => v !== poly[(i + poly.length - 1) % poly.length]);
      tris.push(...earClip(pts, clean));
    } else for (let i = 0; i + 1 < band.length; i++) {
      const y0 = band[i], y1 = band[i + 1];
      if (y1 > o.sill + 1e-9) continue;
      const cuts = y0 < 1e-9 ? along(bottomCuts, o.x0, o.x1) : [];
      if (cuts.length) tris.push(...earClip(pts, [P(o.x0, y0), ...cuts.map((c) => P(c, 0)), P(o.x1, y0), P(o.x1, y1), P(o.x0, y1)]));
      else quad(P(o.x0, y0), P(o.x1, y0), P(o.x1, y1), P(o.x0, y1));
    }
    // ...and the shoulders an overhanging head sits on: solid from the jamb out to the span, sill to springing
    for (const [xa, xb] of [[o.x0, o.j0], [o.j1, o.x1]]) {
      if (xb - xa < 1e-9) continue;
      for (let i = 0; i + 1 < band.length; i++) {
        const y0 = band[i], y1 = band[i + 1];
        if (y0 >= o.sill - 1e-9 && y1 <= o.springing + 1e-9) quad(P(xa, y0), P(xb, y0), P(xb, y1), P(xa, y1));
      }
    }
    // AN OPENING OPEN TO THE TOP (a flat head at the wall's own top: a notch, where another building's wall takes over
    // -- a nave's west wall where the tower stands): nothing over it
    if (o.springing >= h - 1e-9 && o.curve.every(([, cy]) => Math.abs(cy) < 1e-9)) { x = o.x1; continue; }
    // the arch band: one quad per curve segment, up to the top of the wall. Adjacent quads share the curve's
    // own points, and the outer ones share the jamb edges, so the band has no seam of its own.
    const c = o.curve.map(([cx, cy]) => P(o.at + cx, o.springing + cy));
    // ONE CUT GRID, HERE TOO -- but only where it matters. The band's END verticals stand against a pier,
    // whose edge is broken at every cut; if the band's is not broken at the same heights the two meet as one
    // long edge against several short ones, which is a T-junction: a hairline crack on screen and an open edge
    // in the mesh. The verticals INSIDE the band touch nothing else and must NOT be cut, or the apex segment
    // (whose top already sits at the crown) ends up cut differently from its neighbour -- which is the same
    // fault the other way round. So each piece is a polygon: the curve segment, up the right side, along the
    // top, down the left side, with the cuts only on an end vertical, fanned from its first corner.
    const cutsAbove = (y) => ownCuts(o).filter((v) => v > y + 1e-9);
    // THE TOP EDGE IS NOT THE ARCH'S BUSINESS. Give every curve segment its own piece running up to the top and
    // the top edge is cut once per segment -- and the top edge, extruded, is a FLOOR: the flat extrados of a
    // vault, the top of an arcade wall. Turn the arches' detail up and every floor in the building multiplied
    // with it, flat as it is. So the masonry over a head is two fans from ONE point on the top edge, over the
    // crown: from there the whole left half of a head (any convex head) is in plain sight, and the right half
    // too, and no diagonal runs along a cut side. The top edge is cut once per opening whatever the detail.
    if (c.length === 2 && cutsAbove(pts[c[0]][1]).length && cutsAbove(pts[c[1]][1]).length && !along(topCuts, o.x0, o.x1).length) {   // a one-segment head (a flat lintel): both sides cut, at the same heights
      const [ax, ay] = pts[c[0]], [bx, by] = pts[c[1]];
      let y0 = Math.max(ay, by);
      for (const yc of cutsAbove(ay)) { quad(P(ax, y0), P(bx, y0), P(bx, yc), P(ax, yc)); y0 = yc; }
      quad(P(ax, y0), P(bx, y0), P(bx, h), P(ax, h));
    } else {
      // ONE POLYGON FOR THE WHOLE HEAD: along the curve, up the right side (broken at the cuts, because that
      // vertical stands against a pier whose edge is broken there too), across the top, down the left side.
      // Ear-clipped, so it is valid however the head bulges, and the top edge is still cut once per opening.
      const [ax, ay] = pts[c[0]], [bx, by] = pts[c[c.length - 1]];
      const lx = o.x0, rx = o.x1;                       // the span (a horseshoe's is wider than its jambs)
      const band = [...c, P(rx, by),
                    ...cutsAbove(by).map((yc) => P(rx, yc)), P(rx, h), ...along(topCuts, rx, lx).map((cx) => P(cx, h)),
                    P(lx, h), ...cutsAbove(ay).slice().reverse().map((yc) => P(lx, yc)), P(lx, ay)];
      const dedup = band.filter((v, i) => v !== band[(i + band.length - 1) % band.length]);
      tris.push(...earClip(pts, dedup));
    }
    // ...and the strip above the crown is already covered by those quads, because they run to h.
    x = o.x1;
  }
  if (x < w - 1e-9) solid(x, w);

  return { ...closeFace(pts, tris), w, h, openings: ops };
}

// THE BOUNDARY IS DERIVED, NOT DECLARED. Every edge that belongs to exactly one triangle is on the face's
// border -- that is the definition -- so the loops are chained out of those edges rather than written by
// hand. Two things follow, and both matter: the sides of the extrusion meet the front face's edges exactly
// (they are built from the same edges), and an opening that reaches the floor is handled without a special
// case: it is simply a notch in the one outer loop rather than a hole of its own. Every face builder ends
// here -- a wall, a vault's section, a flight of steps -- so they all extrude the same way.
export function closeFace(pts, tris) {
const use = new Map();
for (const [a, b, c] of tris) {
  for (const [p0, p1] of [[a, b], [b, c], [c, a]]) {
    const k = p0 < p1 ? `${p0},${p1}` : `${p1},${p0}`;
    const e = use.get(k);
    if (e) e.n++; else use.set(k, { n: 1, a: p0, b: p1 });
  }
}
// from -> [to]: a vertex may carry more than one border edge (two loops pinching at a corner), so the
// edges are CONSUMED as they are walked rather than looked up once
const out = new Map();
let left = 0;
for (const e of use.values()) {
  if (e.n !== 1) continue;
  if (!out.has(e.a)) out.set(e.a, []);
  out.get(e.a).push(e.b);
  left++;
}
const loops = [];
while (left > 0) {
  let start0 = -1;
  for (const [v, list] of out) if (list.length) { start0 = v; break; }
  if (start0 < 0) break;
  const loop = [];
  let v = start0;
  for (;;) {
    const list = out.get(v);
    if (!list || !list.length) break;
    loop.push(v);
    v = list.pop();
    left--;
    if (v === start0) break;
  }
  if (loop.length > 2) loops.push(loop);
}
// a loop's signed area says which it is: the face's outside turns one way, a hole in it the other
const area = (loop) => {
  let s2 = 0;
  for (let i = 0; i < loop.length; i++) {
    const [x0, y0] = pts[loop[i]], [x1, y1] = pts[loop[(i + 1) % loop.length]];
    s2 += x0 * y1 - x1 * y0;
  }
  return s2 / 2;
};
const rings = loops.map((loop) => ({ loop, hole: area(loop) < 0 }));
  return { pts, tris, rings };
}

// ---- extrusion ---------------------------------------------------------------------------------------------
// A face becomes a solid by mapping every face point to a FRONT and a BACK point and closing the sides. The
// mapping is the only thing that differs between a straight wall and a bay of a round building, so it is a
// function: map(x, y, side) -> [X, Y, Z]. Both sides use the SAME face points, so the front, the back and
// every reveal share their edges by construction.
// WHICH SURFACES TO EMIT. A solid is the default and the right answer for a wall, but most of a building is
// never seen from inside its own masonry: the cavea is a mass of concrete 28 metres thick whose only visible
// surfaces are the steps on top of it, the soffit over a tunnel, and the two walls that tunnel runs between.
// So a part may ask for just those. `sides` are the two ends of the sweep (for a wedge, its radial planes --
// which is exactly what a passage's side walls are), and the boundary walls are tagged by the face that made
// them, so "top" takes the treads and risers and "base" the flat underside.
//   A part built this way is a SHELL: it has boundary edges by design, and the self-check reports them as
// boundary rather than as holes. What it must still satisfy is everything else -- no T-junction, no edge used
// by three triangles, and its neighbours' vertices landing exactly on its own.
export function extrude(face, map, m = mesh(), emit = null) {
  // caps: true for both ends of the sweep, or "front"/"back" for one of them -- a landing's inner wall is
  // masonry and its outer one is where the flights arrive, so the two are not the same decision.
  const capF = !emit || emit.caps === true || emit.caps === "front";
  const capB = !emit || emit.caps === true || emit.caps === "back";
  const want = !emit || !emit.walls ? null : new Set(emit.walls);
  const front = face.pts.map(([x, y]) => m.vert(...map(x, y, 0)));
  const back = face.pts.map(([x, y]) => m.vert(...map(x, y, 1)));
  for (const [a, b, c] of face.tris) {
    if (capF) m.tri(front[a], front[b], front[c]);   // the face you see
    if (capB) m.tri(back[c], back[b], back[a]);      // ...and its back, wound the other way
  }
  for (const { loop, hole } of face.rings) {   // the outside of the block, and the reveal through each opening
    for (let i = 0; i < loop.length; i++) {
      const a = loop[i], b = loop[(i + 1) % loop.length];
      if (want && !want.has(face.tag?.get(a < b ? `${a},${b}` : `${b},${a}`) ?? "wall")) continue;
      // (the face's triangles all turn one way, so its border edges run with the masonry on the same side
      //  whether they bound the outside or a hole: ONE winding serves both. Flipping it for holes turned every
      //  reveal to face into the stone -- invisible on a double-sided material, wrong on anything else.)
      void hole;
      m.quad(front[b], front[a], back[a], back[b]);
    }
  }
  return m;
}

// AN ANNULAR BARREL VAULT, one bay of it. The face is the vault's CROSS-SECTION -- x runs outward across the
// corridor, y up from the springing line -- and the "extrusion" sweeps it between the bay's two radial planes.
// So a vault is the same machinery as a wall: a face with an opening in it (the opening being the void under
// the vault, its head the vault's own curve), extruded by a different map. Its ends lie on the radial planes,
// so the wedges meet their neighbours exactly, as the arcade's bays do.
// `centre` turns the wedge within its bay, so a piece can sit beside the bay's middle rather than on it --
// which is what the seating either side of a vomitorium's slot needs.
export const sweep = (rIn, halfAngle, y0, centre = 0) => (x, y, side) => {
  const r = rIn + x, th = centre + (side ? 1 : -1) * halfAngle;
  return [r * Math.sin(th), y0 + y, r * Math.cos(th)];
};

// A PASSAGE WITH PARALLEL SIDES. A wedge is the wrong shape for something you walk along: cut one out of a
// ring and it is half again as wide where it leaves the building as where it arrives. This map runs the face
// out along ONE ray -- x is the distance along it, the two sides are a fixed number of metres either side of
// it -- so a corridor built with it is the same width from end to end, and can be made to match the arch it
// starts at. `theta` turns the whole passage within its bay.
export const corridor = (rIn, halfW, y0 = 0, theta = 0) => (x, y, side) => {
  const r = rIn + x, s = (side ? 1 : -1) * halfW;
  return [r * Math.sin(theta) + s * Math.cos(theta), y0 + y, r * Math.cos(theta) - s * Math.sin(theta)];
};

// THE SEATING BESIDE A PARALLEL PASSAGE: a wedge on one side, a straight wall on the other. Its outer edge
// stays on the bay's radial plane, where it must meet the next bay exactly; its inner edge follows the
// passage's own wall. `sign` is which side of the passage it sits on.
export const flank = (rIn, halfBay, halfW, y0 = 0, sign = 1) => (x, y, side) => {
  const r = rIn + x;
  // (the straight side is the one nearer the passage's middle: side 0 for the piece at +x, 1 for the one at -x -- so
  //  side 1 is always the side further along +x, as a wedge's is, and the solid is wound outward as a wedge is)
  if (side === (sign > 0 ? 0 : 1)) {                       // the straight side, against the passage wall
    const s = sign * halfW;
    return [r * Math.sin(0) + s, y0 + y, r * Math.cos(0)];
  }
  const th = sign * halfBay;                               // the radial plane at the bay's edge
  return [r * Math.sin(th), y0 + y, r * Math.cos(th)];
};

// A FLIGHT THAT CLIMBS ALONG THE RING rather than across it. Eleven metres of rise will not fit in a six-metre
// corridor going outward, which is why the stairs to an amphitheatre's upper storey run round it: the steps
// are annular bands, the face's x is arc length at `rArc` and its two sides are the corridor's two walls.
export const along = (rNear, rFar, rArc, y0 = 0, th0 = 0) => (x, y, side) => {
  const th = th0 + x / rArc, r = side ? rNear : rFar;
  return [r * Math.sin(th), y0 + y, r * Math.cos(th)];
};

// a straight wall: the face stands in the xz plane, extruded by its thickness along -z
// ---- the dome ------------------------------------------------------------------------------------------------
// A CLOISTER VAULT over a regular polygon: Florence's is the shape everyone pictures when they hear "dome",
// and it is not a hemisphere -- it is eight curved webs meeting on eight groins, springing from an octagonal
// drum and ending at an oculus the lantern stands on.
//
// The MERIDIAN is the same curve an arch is: the right-hand half of an arch profile over the dome's own span,
// which is exactly how the shape was set out ("quinto acuto" -- the arc struck at four fifths of the span --
// is the pointed profile at spread 0.6). The horizontal section at any height is the SAME polygon shrunk to
// that meridian's radius, so the webs are the strips between successive polygons and the groins are where
// their corners line up: nothing has to be intersected, and the ring closes on itself exactly.
//
// Two shells, an inner and an outer, because that is what the real one is (and what leaves room for the stair
// between them): the inner is the outer's radius less `thickness`, measured horizontally. The oculus is
// closed by the ring between the two shells, the springing by the ring between them at the bottom.
// The meridian's ROWS -- [radius, height] from the springing up -- shared by the shell and by anything laid on
// it (the ribs), so the two are set out on the same heights and meet.
export function domeRows(curve, oculus = 0, base = 0) {
  const pts = [];
  for (const [x, y] of curve) if (x >= -1e-9) pts.push([Math.max(0, x), y]);
  pts.reverse();                                   // ...from the outside in: (radius, 0) first
  if (!pts.length) throw new Error("a dome's profile gave no meridian");
  const rows = [];
  for (let i = 0; i < pts.length; i++) {
    const [r, y] = pts[i];
    if (r < oculus - 1e-9) {
      // stop at the oculus, WHERE THE MERIDIAN CROSSES IT: the lantern stands on it. (Stopping at the last
      // sample outside it and running in flat laid a horizontal ring over the crown, the inner shell's and
      // the outer's on top of each other.)
      const [r0, y0] = pts[i - 1], f = (r0 - oculus) / (r0 - r);
      rows.push([oculus, base + y0 + (y - y0) * f]);
      break;
    }
    rows.push([r, base + y]);
  }
  if (rows.length < 2) throw new Error("a dome needs a meridian with some rise in it");
  return rows;
}

// THE CORNERS of a dome's polygon. A whole dome puts a flat face toward +z, as a ring of bays does. A PART of a
// dome -- `sweep` 0.5 is the SEMIDOME, the conch over an apse -- runs from -sweep/2 to +sweep/2 of a turn about
// +z, so its two ends lie on its own cut (for a semidome, the diameter along x) and the corners count from there.
// `turn` (in faces) turns a whole dome's polygon: -0.5 puts its CORNERS on the axes instead of its faces, which is
// what a dome on pendentives needs -- their crowns, over the four arches, are on the axes.
export function domeCorners(n, sweep = 1, turn = 0) {
  if (sweep >= 1 - 1e-9) return { count: n, closed: true, at: (k) => (k + .5 + turn) * 2 * Math.PI / n, first: (.5 + turn) * 2 * Math.PI / n };
  const segs = Math.max(1, Math.round(n * sweep)), t0 = -Math.PI * sweep, step = 2 * Math.PI * sweep / segs;
  return { count: segs + 1, closed: false, at: (k) => t0 + k * step, first: t0, step };
}

// `thickness` 0 is a SKIN: one surface, closed underneath by a disc and at an oculus by another -- a timber
// roof's cone or an onion over a tower is a shape seen from outside, not two shells of masonry. A part of a dome
// is closed at its cut: a masonry one by the section through its two shells, a skin by the flat of its profile
// (a half-cone roof against a wall has a wall there).
// `door` { width, height, at }: A DOORWAY CUT IN ITS FOOT -- whole faces of its polygon (as many as come nearest to
// `width` at the springing), centred on the angle `at` (+x unless said), up to `height`: the web and the soffit left
// out there, the two jambs closed by the section through the shell, a lintel under its head. One dome with a hole in
// it, as a snow house or a tipi is -- not a band under a cap, whose two meridians (the cut one sampled, the cap's
// true) never met.
export function domeShell(m, { sides = 8, sweep = 1, turn = 0, oculus = 0, thickness, curve, base = 0, cap = true, coffers = null, door = null }) {
  const n = Math.max(3, Math.round(sides));
  const C = domeCorners(n, sweep, turn), N = C.count;
  let rows = domeRows(curve, oculus, base);
  // (a row spliced in at height y, where the meridian crosses it, so the door's head is a row of its own)
  const splice = (rs, y) => {
    const j = rs.findIndex(([, ry]) => Math.abs(ry - y) < 1e-6);
    if (j >= 0) return [rs, j];
    const i = rs.findIndex(([, ry], q) => q + 1 < rs.length && ry < y && rs[q + 1][1] > y);
    if (i < 0) throw new Error(`a door ${(y - base).toFixed(2)} m high does not fit under the dome`);
    const [r0, y0] = rs[i], [r1, y1] = rs[i + 1], f = (y - y0) / (y1 - y0);
    return [[...rs.slice(0, i + 1), [r0 + (r1 - r0) * f, y], ...rs.slice(i + 1)], i + 1];
  };
  let dO = 0, dK = new Set(), k0 = 0, df = 0;
  if (door) {
    if (!C.closed) throw new Error("a door is cut in a whole dome's foot");
    if (coffers) throw new Error("a dome with a door has no coffers");
    df = Math.max(1, Math.min(N - 1, Math.round(door.width / (2 * rows[0][0] * Math.sin(Math.PI / N)))));
    k0 = ((Math.round((door.at ?? Math.PI / 2) * N / (2 * Math.PI) - df / 2 - .5 - turn) % N) + N) % N;
    dK = new Set(Array.from({ length: df }, (_, j) => (k0 + j) % N));
    [rows, dO] = splice(rows, base + door.height);
  }
  const inDoor = (i, k, below) => i < below && dK.has(k);
  const ring = (r, y) => Array.from({ length: N }, (_, k) => {
    const t = C.at(k);
    return m.vert(r * Math.sin(t), y, r * Math.cos(t));   // (at r = 0 every corner is ONE vertex: the tip)
  });
  const edges = C.closed ? N : N - 1;
  const outs = rows.map(([r, y]) => ring(r, y));
  for (let i = 0; i + 1 < rows.length; i++) for (let k = 0; k < edges; k++) {
    if (inDoor(i, k, dO)) continue;
    const k2 = (k + 1) % N;
    m.quad(outs[i][k], outs[i][k2], outs[i + 1][k2], outs[i + 1][k]);        // the web, outside
  }
  const lo = 0, hi = rows.length - 1;
  if (!(thickness > 0)) {                          // a skin: a disc under it, and one over an oculus
    if (cap) {
      const c0 = m.vert(0, rows[lo][1], 0), c1 = m.vert(0, rows[hi][1], 0);
      for (let k = 0; k < edges; k++) {
        const k2 = (k + 1) % N;
        m.tri(c0, outs[lo][k2], outs[lo][k]);
        if (rows[hi][0] > 1e-9) m.tri(c1, outs[hi][k], outs[hi][k2]);
      }
      if (!C.closed) {                             // ...and the flat of the profile at each end of the cut
        for (const [k, flip] of [[0, false], [N - 1, true]]) {
          // the half-profile, as a polygon in its own plane (r out, y up, counter-clockwise): the axis at the
          // springing, out along the meridian, and back to the axis at the top. Ear-clipped in that plane, whose
          // counter-clockwise side faces back along the cut at the first end, so the far end is turned over.
          const top = rows[hi][0] > 1e-9;
          const flat = [[0, rows[lo][1]], ...rows, ...(top ? [[0, rows[hi][1]]] : [])];
          const ids = [c0, ...rows.map((_, i) => outs[i][k]), ...(top ? [c1] : [])];
          const keep = ids.map((v, i) => i === 0 || v !== ids[i - 1]);
          const pts2 = flat.filter((_, i) => keep[i]), vs = ids.filter((_, i) => keep[i]);
          if (vs[vs.length - 1] === vs[0]) { vs.pop(); pts2.pop(); }
          for (const [p, q, r2] of earClip(pts2, vs.map((_, i) => i))) {
            if (flip) m.tri(vs[r2], vs[q], vs[p]); else m.tri(vs[p], vs[q], vs[r2]);
          }
        }
      }
    }
    return m;
  }
  // the inner shell: `thickness` in from the outer one. Over an oculus that is measured across, at every row;
  // a dome CLOSED at its crown has no across there, so its inner shell is the outer one scaled in by the
  // thickness both ways -- as thick at the crown as at the springing, and never through its own tip.
  const R0 = rows[lo][0], H0 = rows[hi][1] - base;
  let inner = rows[hi][0] > 1e-9
    ? rows.map(([r, y]) => [Math.max(r - thickness, .02), y])
    : rows.map(([r, y]) => [r * Math.max(.05, 1 - thickness / R0), base + (y - base) * Math.max(.05, 1 - thickness / H0)]);
  let dI = 0;
  if (door) {
    // the soffit gets its own row at the door's head (a closed crown's soffit is the web scaled, rows and all: the
    // web's door row comes down with it, a little under the head, and is dropped for the one at the head)
    if (rows[hi][0] <= 1e-9) inner = inner.filter((_, i) => i !== dO);
    [inner, dI] = splice(inner, base + door.height);
  }
  // THE COFFERED BAND, if there is one: its rows are spliced into the soffit's own (by arc length up the inner
  // meridian, `from` to `to`), and the strip between them is left to cofferedSurface -- whose cells carry every
  // one of the ring's stations on their edges, so the plain soffit above and below meets it exactly.
  let band = null;
  if (coffers) {
    const len = [0];
    for (let i = 1; i < inner.length; i++) len.push(len[i - 1] + Math.hypot(inner[i][0] - inner[i - 1][0], inner[i][1] - inner[i - 1][1]));
    const total = len[len.length - 1], sA = coffers.from * total, sB = coffers.to * total;
    const pointAt = (sl) => {
      let i = 1; while (i < len.length - 1 && len[i] < sl) i++;
      const f = (sl - len[i - 1]) / Math.max(1e-12, len[i] - len[i - 1]);
      return [inner[i - 1][0] + (inner[i][0] - inner[i - 1][0]) * f, inner[i - 1][1] + (inner[i][1] - inner[i - 1][1]) * f];
    };
    const kv = Math.max(1, coffers.kv ?? 1), nv = Math.max(1, Math.round(coffers.rows));
    const samples = Array.from({ length: nv * kv + 1 }, (_, j) => pointAt(sA + (sB - sA) * j / (nv * kv)));
    const below = inner.filter((_, i) => len[i] < sA - 1e-6), above = inner.filter((_, i) => len[i] > sB + 1e-6);
    band = { start: below.length, end: below.length + nv * kv, samples, nv, kv };
    inner = [...below, ...samples, ...above];
  }
  const ins = inner.map(([r, y]) => ring(r, y));
  for (let i = 0; i + 1 < inner.length; i++) {
    if (band && i >= band.start && i < band.end) continue;
    for (let k = 0; k < edges; k++) {
      if (inDoor(i, k, dI)) continue;
      const k2 = (k + 1) % N;
      m.quad(ins[i + 1][k], ins[i + 1][k2], ins[i][k2], ins[i][k]);          // ...and its soffit, wound the other way
    }
  }
  if (band) {
    const nu = Math.max(1, Math.round(coffers.count)), ku = edges / nu;
    if (Math.abs(ku - Math.round(ku)) > 1e-9) throw new Error(`${nu} coffers round do not divide the dome's ${edges} faces`);
    if (!(coffers.depth < thickness * .8)) throw new Error(`coffers ${coffers.depth}m deep in a shell ${thickness}m thick`);
    const step = C.closed ? 2 * Math.PI / N : C.step;
    const ang = (u) => (Number.isInteger(u) ? C.at(u % N) : C.at(0) + u * step);
    const mer = (v) => {                           // the band's meridian, between its samples
      const j = Math.max(0, Math.min(band.samples.length - 2, Math.floor(v))), f = v - j;
      const [r0, y0] = band.samples[j], [r1, y1] = band.samples[j + 1];
      return f === 0 ? [r0, y0] : [r0 + (r1 - r0) * f, y0 + (y1 - y0) * f];
    };
    const S = (u, v) => { const [r, y] = mer(v), t = ang(u); return [r * Math.sin(t), y, r * Math.cos(t)]; };
    const Nn = (u, v) => {                         // into the stone: square to the meridian, away from the axis
      const [ra, ya] = mer(Math.max(0, v - .05)), [rb, yb] = mer(Math.min(band.samples.length - 1, v + .05));
      let nr = yb - ya, ny = -(rb - ra); const l = Math.hypot(nr, ny) || 1; nr /= l; ny /= l;
      const t = ang(u);
      if (coffers.toward === undefined || coffers.toward === null) return [nr * Math.sin(t), ny, nr * Math.cos(t)];
      // IN PERSPECTIVE: the pockets sunk along the line of sight from a point on the axis (`toward`, a height
      // above the springing -- the Pantheon's are aimed at the middle of its floor), so from there every
      // coffer's sides are seen edge-on and only its stepped ledges show, which is how the real ones are cut
      const p = S(u, v), dx = p[0], dy = p[1] - (base + coffers.toward), dz = p[2], l2 = Math.hypot(dx, dy, dz) || 1;
      const dir = [dx / l2, dy / l2, dz / l2], along = dir[0] * nr * Math.sin(t) + dir[1] * ny + dir[2] * nr * Math.cos(t);
      return dir.map((c) => c / Math.max(.3, along));    // (so `depth` is still measured square to the surface)
    };
    cofferedSurface(m, S, Nn, { nu, nv: band.nv, ku: Math.round(ku), kv: band.kv, frame: coffers.frame, step: coffers.step,
                                steps: coffers.steps, depth: coffers.depth });
  }
  const his = ins.length - 1;
  if (cap) {
    for (let k = 0; k < edges; k++) {
      const k2 = (k + 1) % N;
      if (!dK.has(k)) m.quad(ins[0][k], ins[0][k2], outs[lo][k2], outs[lo][k]);   // the springing ring (none across the doorway)
      m.quad(outs[hi][k], outs[hi][k2], ins[his][k2], ins[his][k]);          // ...and the oculus
    }
  }
  if (door) {
    // the doorway's JAMBS -- the section through both shells, from the floor to the head, at its two corners (the
    // first faces back against the faces before it, the second on against those after) -- and its LINTEL, facing down
    const jamb = (k, flip) => {
      const poly = [...rows.slice(0, dO + 1), ...inner.slice(0, dI + 1).reverse()];
      const vs = [...outs.slice(0, dO + 1).map((o) => o[k]), ...ins.slice(0, dI + 1).reverse().map((o) => o[k])];
      for (const [p, q, r2] of earClip(poly, vs.map((_, i) => i))) { if (flip) m.tri(vs[r2], vs[q], vs[p]); else m.tri(vs[p], vs[q], vs[r2]); }
    };
    jamb(k0, true); jamb((k0 + df) % N, false);
    for (const k of dK) { const k2 = (k + 1) % N; m.quad(ins[dI][k], ins[dI][k2], outs[dO][k2], outs[dO][k]); }
  }
  if (!C.closed) {                                 // the section through both shells at the cut: one polygon per end
    for (const [k, flip] of [[0, false], [N - 1, true]]) {
      const poly = [...rows.map(([r, y]) => [r, y]), ...inner.slice().reverse()];
      const vs = [...outs.map((o) => o[k]), ...ins.slice().reverse().map((o) => o[k])];
      for (const [p, q, r2] of earClip(poly, vs.map((_, i) => i))) {
        if (flip) m.tri(vs[r2], vs[q], vs[p]); else m.tri(vs[p], vs[q], vs[r2]);
      }
    }
  }
  return m;
}

// A RIB ALONG A PATH: a box section carried along a line of points, each with its own frame -- `n` the way the
// rib stands out (off a dome's back, down from a vault's soffit), `b` across it. The section runs from `v0` to
// `v1` along n (a vault rib reaches back INTO the masonry, so no slit shows between it and the webs either
// side of the crease it covers) and is `width` across. Wound outward whichever way the path runs.
// `u0`/`u1` (default the width centred) put the section to one side of the path: a wall rib hangs on its own
// bay's side of the arch, so it neither pokes through the wall nor lies on top of the next bay's.
export function ribAlong(m, path, { width, v0 = 0, v1, u0 = -width / 2, u1 = width / 2 }) {
  const sec = [[u0, v0], [u1, v0], [u1, v1], [u0, v1]];
  const rings = path.map(({ p, n, b }) => sec.map(([u, v]) => m.vert(p[0] + b[0] * u + n[0] * v, p[1] + b[1] * u + n[1] * v, p[2] + b[2] * u + n[2] * v)));
  const P0 = path[0], P1 = path[Math.min(1, path.length - 1)];
  const T = [P1.p[0] - P0.p[0], P1.p[1] - P0.p[1], P1.p[2] - P0.p[2]];
  const bn = [P0.b[1] * P0.n[2] - P0.b[2] * P0.n[1], P0.b[2] * P0.n[0] - P0.b[0] * P0.n[2], P0.b[0] * P0.n[1] - P0.b[1] * P0.n[0]];
  const flip = bn[0] * T[0] + bn[1] * T[1] + bn[2] * T[2] > 0;
  const quad = (a, b, c, d) => flip ? m.quad(d, c, b, a) : m.quad(a, b, c, d);
  for (let i = 0; i + 1 < rings.length; i++) for (let c = 0; c < 4; c++) {
    const c2 = (c + 1) % 4;
    quad(rings[i][c], rings[i + 1][c], rings[i + 1][c2], rings[i][c2]);
  }
  quad(rings[0][0], rings[0][1], rings[0][2], rings[0][3]);                                   // its foot
  const top = rings[rings.length - 1];
  quad(top[3], top[2], top[1], top[0]);                                                        // ...and its head
  return m;
}

// THE RIBS, laid ON a dome: an addition, not a property of it -- a plain dome has none, Florence's has eight
// in white marble against the tile, St Peter's sixteen. Each is a box section carried up the meridian at its
// own angle, on the dome's own rows, standing on the dome's OUTER SURFACE at that angle: on a corner (a groin)
// that is the meridian's radius, between two corners it is the flat face's, which is nearer the axis. On a
// whole dome they stand on the groins unless `turn`ed; on a semidome they divide it, and none stands on the cut.
export function domeRibs(m, { sides, sweep = 1, domeTurn = 0, curve, oculus = 0, base = 0, count = sides, turn = 0, width, depth }) {
  const n = Math.max(3, Math.round(sides));
  const C = domeCorners(n, sweep, domeTurn);
  // a rib stops where the shell grows narrower than the rib: at a tip, every rib would meet every other
  const rows = domeRows(curve, oculus, base).filter(([r]) => r > width * 1.5);
  if (rows.length < 2) return m;
  const face = C.closed ? 2 * Math.PI / n : C.step;
  const angles = C.closed
    ? Array.from({ length: count }, (_, k) => C.at(0) + (k + turn) * 2 * Math.PI / count)
    : Array.from({ length: Math.max(0, count) }, (_, k) => C.first + (k + .5 + turn) * 2 * Math.PI * sweep / count);
  for (const t of angles) {
    const off = (((t - C.first) % face) + face) % face - face / 2;           // angle from the face's middle
    const onFace = Math.cos(face / 2) / Math.cos(off);                      // the surface's radius there, per unit
    const ct = Math.cos(t), st = Math.sin(t);
    ribAlong(m, rows.map(([r, y]) => ({ p: [r * onFace * st, y, r * onFace * ct], n: [st, 0, ct], b: [ct, 0, -st] })),
             { width, v0: 0, v1: depth });
  }
  return m;
}

// THE RIBS OF A RIB VAULT, laid under a groin vault (the Gothic bay): the two DIAGONALS along its groins, and
// if asked the arches round its four sides -- `wall` ribs on the wall arches, which a neighbouring bay shares
// as its own transverse rib. Set out from groinGeometry, the vault's own numbers. Each hangs `depth` below
// the soffit and reaches as far up into the webs, so no slit shows either side of it.
export function groinRibs(m, { width, length, curveX, curveZ, springing, rib, wallRib = null }) {
  const g = groinGeometry({ width, length, curveX, curveZ, springing });
  const t = [...g.groinT].reverse();                         // corner (1) to the middle (0)
  for (const [sx, sz] of [[1, 1], [1, -1]]) {
    // one diagonal, corner to corner through the middle
    const pts = [...t.map((f) => [-sx * f * g.A, g.G(f), -sz * f * g.B]), ...t.slice(0, -1).reverse().map((f) => [sx * f * g.A, g.G(f), sz * f * g.B])];
    const d = [2 * sx * g.A, 0, 2 * sz * g.B], l = Math.hypot(d[0], d[2]), bh = [-d[2] / l, 0, d[0] / l];
    ribAlong(m, pts.map((p) => ({ p, n: [0, -1, 0], b: bh })), { width: rib.width, v0: -rib.depth, v1: rib.depth });
  }
  if (wallRib) for (const [curve, along, other] of [[curveX, "x", g.B], [curveZ, "z", g.A]]) {
    for (const side of [-1, 1]) {
      const pts = curve.map(([c, y]) => along === "x" ? [c, springing + y, side * other] : [side * other, springing + y, c]);
      const path = pts.map((p, i) => {
        const q = pts[Math.min(i + 1, pts.length - 1)], o = pts[Math.max(i - 1, 0)];
        const tx = along === "x" ? q[0] - o[0] : q[2] - o[2], ty = q[1] - o[1], l = Math.hypot(tx, ty) || 1;
        const nx = ty / l, ny = -tx / l;                     // square to the arch, pointing down into the opening
        return { p, n: along === "x" ? [nx, ny, 0] : [0, ny, nx], b: along === "x" ? [0, 0, 1] : [1, 0, 0] };
      });
      // on the bay's own side of the wall arch (inside is toward the bay's middle, -side along b)
      const inward = side > 0 ? [-wallRib.width, 0] : [0, wallRib.width];
      ribAlong(m, path, { width: wallRib.width, v0: -wallRib.depth, v1: wallRib.depth, u0: inward[0], u1: inward[1] });
    }
  }
  return m;
}

// ---- pendentives and the sail vault ----------------------------------------------------------------------
// HOW A ROUND DOME STANDS ON A SQUARE: four arches over the sides of the square, and between them four
// PENDENTIVES -- the spherical triangles that turn the square into the circle the dome springs from. They are
// all ONE sphere, the one through the square's four corners (radius span/sqrt2, centred on the axis at the
// arches' springing): where it stands over the square's sides it is cut away by the arches (and those cuts are
// exactly the arches' semicircles), and it is cut off level where it reaches the circle inscribed in the
// square, `span`/2 across, at the arches' crowns. That circle is the dome's springing. Hagia Sophia's dome,
// 31m across, stands on four of them.
//   Left whole -- not cut off at the circle -- the same sphere is the SAIL VAULT (a domical vault over a square
// bay, the Byzantine aisle's roof): `sail: true`.
//   Its stations round the axis are a dome's with its corners ON the axes (a dome of the same `sides` turned
// by -0.5), so the dome standing on it meets it point for point. It is a surface -- the soffit you see from
// below -- so it is a shell; its back is inside the masonry.
export function pendentives(m, { span, springing, sides, rows = 4, sail = false }) {
  const n = Math.max(4, Math.round(sides / 4) * 4), a = span / 2, Rp = a * Math.SQRT2;
  const y = (r) => springing + Math.sqrt(Math.max(0, Rp * Rp - r * r));
  const centre = [0, springing, 0];
  const ring = [];
  for (let k = 0; k <= n; k++) {
    const t = k * 2 * Math.PI / n, st = Math.sin(t), ct = Math.cos(t);
    const rEdge = a / Math.max(Math.abs(st), Math.abs(ct));           // out along this ray to the square's side
    const r0 = sail ? 0 : a;
    ring.push(Array.from({ length: rows + 1 }, (_, j) => {
      const r = r0 + (rEdge - r0) * j / rows;
      return { i: m.vert(r * st, y(r), r * ct), p: [r * st, y(r), r * ct] };
    }));
  }
  // facing the centre of the sphere: that is the side you stand under
  const tri = (A, B, C) => {
    const u = [B.p[0] - A.p[0], B.p[1] - A.p[1], B.p[2] - A.p[2]], v = [C.p[0] - A.p[0], C.p[1] - A.p[1], C.p[2] - A.p[2]];
    const nn = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
    const g = [(A.p[0] + B.p[0] + C.p[0]) / 3 - centre[0], (A.p[1] + B.p[1] + C.p[1]) / 3 - centre[1], (A.p[2] + B.p[2] + C.p[2]) / 3 - centre[2]];
    if (nn[0] * g[0] + nn[1] * g[1] + nn[2] * g[2] > 0) m.tri(A.i, C.i, B.i); else m.tri(A.i, B.i, C.i);
  };
  for (let k = 0; k < n; k++) for (let j = 0; j < rows; j++) {
    const a0 = ring[k][j], a1 = ring[k][j + 1], b0 = ring[k + 1][j], b1 = ring[k + 1][j + 1];
    tri(a0, b0, b1); tri(a0, b1, a1);
  }
  return m;
}

// A RECTANGULAR FRAME, closed: the ring beam an entablature is round a peristyle -- solid between an outer
// rectangle and an inner one, open to the sky (or to the roof's underside) in the middle.
export function frame(m, [ox, oz], [ix, iz], y0, y1) {
  const O = [[-ox, -oz], [ox, -oz], [ox, oz], [-ox, oz]], I = [[-ix, -iz], [ix, -iz], [ix, iz], [-ix, iz]];
  const v = (c, y) => c.map(([x, z]) => m.vert(x, y, z));
  const oL = v(O, y0), oH = v(O, y1), iL = v(I, y0), iH = v(I, y1);
  for (let k = 0; k < 4; k++) {
    const k2 = (k + 1) % 4;
    m.quad(oL[k2], oL[k], oH[k], oH[k2]);                 // the outer face (as a box's sides)
    m.quad(iL[k], iL[k2], iH[k2], iH[k]);                 // the inner face, turned to look in
    m.quad(oH[k2], oH[k], iH[k], iH[k2]);                 // the top, between the two outlines
    m.quad(oL[k], oL[k2], iL[k2], iL[k]);                 // ...and the soffit
  }
  return m;
}

// ---- the groin vault -----------------------------------------------------------------------------------------
// TWO BARRELS CROSSING, which is what every Gothic bay is: the vault over a rectangular bay whose soffit meets
// each of its four walls along that wall's own arch, and whose GROINS run diagonally from corner to corner
// where the two barrels cut each other.
//
// It needs no intersection to be computed. Over the bay's plan the soffit is simply the HIGHER of the two
// barrels -- y(u, v) = max(across(u), along(v)) -- and that single line is the whole shape: at a wall one of
// the two is at the springing, so the other draws the wall arch; on the diagonal the two are equal, and that
// is the groin. (The LOWER of the two is the cloister vault, the dome's shape, which is why the two vaults
// look like each other's negative.)
//
// The solid is that soffit below, a flat extrados at `top` above (the floor or roof it carries), and the four
// spandrels between the wall arches and that extrados. Closed, welded, and its boundary is exactly the arch
// the wall beside it was built with.
// FOUR WEBS, NOT A GRID. Split the bay by its two diagonals -- a square divided by an X -- and each of the four
// triangles is one WEB: the barrel that springs from that wall, running in from the wall to the groins. A web
// follows its wall's arch vertically (its edge on the wall IS that arch, point for point, so it meets the wall
// face below with no T-junction), and in the other direction it runs in straight lines from the wall to the
// groin -- flat when the two arches rise alike, sloping to meet the crossing web when they do not (the higher
// of the two sets the groin, as a builder stilts the lower arch). The groins are where two webs MEET, so the
// points on them are made once, from both webs' stations together, and both webs use them: the crease is an
// edge of the mesh, not something a grid cell folds across.
//   (It was a grid over the whole bay sampled from max(across, along): every cell the diagonal crossed was
// one quad bent over the groin, and the groin came out a zigzag.)
// THE GROIN'S OWN NUMBERS, shared by the vault and by the ribs laid along it, so the two cannot disagree: each
// arch's stations, the one canonical list of groin stations, and the groin's height at a station.
export function groinGeometry({ width, length, curveX, curveZ, springing }) {
  const A = width / 2, B = length / 2;
  // a profile's height at a signed fraction u of its half-span (-1..1): the curve runs from -half to +half
  const heightAt = (curve, u) => {
    const half = Math.abs(curve[0][0]), x = u * half;
    for (let i = 0; i + 1 < curve.length; i++) {
      const [x0, y0] = curve[i], [x1, y1] = curve[i + 1];
      if ((x >= x0 - 1e-12 && x <= x1 + 1e-12) || (x >= x1 - 1e-12 && x <= x0 + 1e-12)) {
        const f = Math.abs(x1 - x0) < 1e-12 ? 0 : (x - x0) / (x1 - x0);
        return y0 + (y1 - y0) * Math.max(0, Math.min(1, f));
      }
    }
    return 0;
  };
  for (const [c, half] of [[curveX, A], [curveZ, B]]) {
    for (let i = 0; i + 1 < c.length; i++) if (c[i + 1][0] < c[i][0] - 1e-9)
      throw new Error("a groin vault needs a head that runs steadily across its span (no horseshoe, no cusp turning back)");
    if (Math.abs(c[0][0] + half) > 1e-9) throw new Error("a groin's head does not span its bay");
  }
  // each web's own stations (as signed fractions of its half-span), and the groin's: both sets together
  const stX = curveX.map(([x]) => x / A), stZ = curveZ.map(([z]) => z / B);
  // ONE LIST of groin stations, which every web snaps to: two arches' stations a hair apart (a tenth of a
  // millimetre on a 3m half-span) are one point, and the same fraction reached from either web must be the same
  // number, or the two sides of the groin round to different sides of the weld grid and never meet.
  // (the middle of the bay is always one of them: all four groins meet there, even when neither arch has a
  //  station on its crown line -- an odd number of segments -- and without it the webs leave a hole there)
  const groinT = [0];
  for (const t of [...stX, ...stZ].map(Math.abs).sort((p, q) => p - q)) {
    if (!groinT.length || t - groinT[groinT.length - 1] > 1e-4) groinT.push(t);
  }
  const canon = (s) => { const t = Math.abs(s); let best = t, d = 2e-4; for (const g of groinT) if (Math.abs(g - t) < d) { d = Math.abs(g - t); best = g; } return Math.sign(s) * best; };
  const G = (t) => springing + Math.max(heightAt(curveX, t), heightAt(curveZ, t));   // the groin at |fraction| t
  return { A, B, heightAt, stX, stZ, groinT, canon, G };
}

export function groinVault(m, { width, length, curveX, curveZ, springing, top }) {
  const { A, B, heightAt, stX, stZ, groinT, canon, G } = groinGeometry({ width, length, curveX, curveZ, springing });
  // THE FOUR WEBS, each set out in its own frame: `s` runs along its wall (-1..1), `d` from the wall (0) in to
  // the middle of the bay (1); the groins are |s| = 1 - d. `at(s, d)` is the plan point, `curve` the wall's arch.
  const webs = [
    { curve: curveX, st: stX, at: (s, d) => [s * A, -B * (1 - d)] },    // the wall at -z, its arch spans x
    { curve: curveZ, st: stZ, at: (s, d) => [A * (1 - d), s * B] },     // +x
    { curve: curveX, st: stX, at: (s, d) => [-s * A, B * (1 - d)] },    // +z
    { curve: curveZ, st: stZ, at: (s, d) => [-A * (1 - d), -s * B] },   // -x
  ];
  const wallEdges = [];
  for (const w of webs) {
    const wallPt = (s) => { const [x, z] = w.at(s, 0); return m.vert(x, springing + heightAt(w.curve, s), z); };
    const groinPt = (s0) => { const s = canon(s0); const [x, z] = w.at(s, 1 - Math.abs(s)); return m.vert(x, G(Math.abs(s)), z); };
    // every groin point, in order along this web's two groins (s from -1 through 0 to +1)
    const gs = [...groinT.filter((t) => t > 0).map((t) => -t).reverse(), ...groinT].filter((v, i, l) => i === 0 || v !== l[i - 1]);
    const edge = w.st.map(wallPt);
    wallEdges.push(edge);
    for (let i = 0; i + 1 < w.st.length; i++) {
      const s0 = w.st[i], s1 = w.st[i + 1];
      // the strip between two of the wall's stations: its two wall points, then back along the groin through
      // every groin point between them (both webs' stations, and the crown of the bay if the strip spans it)
      const between = gs.filter((s) => s > canon(s0) + 1e-12 && s < canon(s1) - 1e-12);
      const poly = [edge[i], edge[i + 1], groinPt(s1), ...between.slice().reverse().map(groinPt), groinPt(s0)];
      let loop = poly.filter((v, k) => k === 0 || v !== poly[k - 1]);   // (a corner of the bay is both a
      if (loop[loop.length - 1] === loop[0]) loop.pop();                  //  wall point and a groin point)
      // The strip is convex in plan, so it is a fan -- but not from a corner of the bay, which lies ON the
      // groin line with the groin's own points and would fan into slivers of no area. Wound to face DOWN.
      if (Math.abs(s0) > 1 - 1e-12) loop = [...loop.slice(1), loop[0]];
      for (let k = 1; k + 1 < loop.length; k++) m.tri(loop[0], loop[k], loop[k + 1]);
    }
  }
  // the extrados: one flat slab at `top`, fanned from its middle so each side carries the points its spandrel has
  const topRow = (e) => wallEdges[e].map((v, i) => {
    const [x, z] = webs[e].at(webs[e].st[i], 0);
    return m.vert(x, top, z);
  });
  const tops = [0, 1, 2, 3].map(topRow);
  const mid = m.vert(0, top, 0);
  for (const row of tops) for (let i = 0; i + 1 < row.length; i++) m.tri(mid, row[i + 1], row[i]);
  // ...and the spandrel over each wall arch, between the soffit's own edge and that slab
  for (let e = 0; e < 4; e++) for (let i = 0; i + 1 < wallEdges[e].length; i++) {
    m.quad(wallEdges[e][i], tops[e][i], tops[e][i + 1], wallEdges[e][i + 1]);
  }
  return m;
}

// ---- stairs that fly: a flight with its own soffit, straight or helical ------------------------------------
// A STAIR THAT IS NOT A MASS. The seating and the vomitorium flights are stepped masses standing on something;
// a baroque stair is not -- each flight SPANS, from landing to landing, on a sloped underside parallel to its
// own pitch (the rampant vault it is built on), and the landings are slabs. So the flight's side profile is the
// zigzag of risers and treads above, and below it a straight line `soffit` under the nosings: every inner
// corner of a step then has exactly `soffit` of stone under it.
//   The profile is cut into one COLUMN PER STEP -- a pentagon, riser, tread, the next riser's foot, and the
// soffit under it -- rather than fanned: a helical map bends x round a circle, and a triangle spanning several
// steps would cut its chord straight through the stair. `h` is the height the flight starts from; it has `n`
// risers of `rise` on treads of `run`, the last tread flush with what it arrives on. The two verticals at its
// ends below the tread line are tagged "joint", which is where a landing's slab meets it.
export function flightFace(n, run, rise, soffit, h = 0, whole = false) {
  const pts = [], seen = new Map(), tris = [];
  const P = (x, y) => {
    const k = `${Math.round(x * Q)},${Math.round(y * Q)}`;
    let i = seen.get(k);
    if (i === undefined) { i = pts.length; pts.push([x, y]); seen.set(k, i); }
    return i;
  };
  const u = (k) => h - soffit + k * rise;            // the soffit under station k
  const t = (k) => h + (k + 1) * rise;               // the tread of step k (t(-1) is where the flight starts)
  if (whole) {
    // `whole`: a STRAIGHT flight's soffit is one plane -- one edge in the section, so one quad under the whole flight,
    // not one a step. The section is fanned from the soffit's HIGH corner: a ray from there to any corner of the
    // steps runs over the soffit and under the inner corners (both are straight lines it meets only at its ends),
    // so every triangle is inside. (A spiral's soffit bends round its newel: it keeps a station a step.)
    const chain = [P(0, u(0)), P(0, h)];
    for (let k = 0; k < n; k++) chain.push(P(k * run, t(k)), P((k + 1) * run, t(k)));
    const b = P(n * run, u(n));
    for (let i = 0; i + 1 < chain.length; i++) tris.push([b, chain[i + 1], chain[i]]);
  } else for (let k = 0; k < n; k++) {
    const col = [P(k * run, u(k)), P((k + 1) * run, u(k + 1)), P((k + 1) * run, t(k)), P(k * run, t(k)), P(k * run, t(k - 1))];
    // fanned from the bottom-RIGHT corner: the left side carries the riser's foot, three points in a line,
    // and a fan from there lays a triangle of no area along it
    for (let j = 2; j + 1 < col.length + 1; j++) tris.push([col[1], col[j], col[(j + 1) % col.length]]);
  }
  const face = closeFace(pts, tris), tag = new Map(), L = n * run;
  const mark = (a, b, v) => tag.set(a < b ? `${a},${b}` : `${b},${a}`, v);
  for (const { loop } of face.rings) for (let i = 0; i < loop.length; i++) {
    const a = loop[i], b = loop[(i + 1) % loop.length], [ax, ay] = pts[a], [bx, by] = pts[b];
    const vert = Math.abs(ax - bx) < 1e-9;
    const onSoffit = (x, y) => Math.abs(y - (h - soffit + x * rise / run)) < 1e-9;
    mark(a, b, vert && Math.abs(ax) < 1e-9 && Math.max(ay, by) <= h + 1e-9 ? "joint-in"      // under the first riser
             : vert && Math.abs(ax - L) < 1e-9 ? "joint-out"                                // under the last tread
             : !vert && onSoffit(ax, ay) && onSoffit(bx, by) ? "base"
             : "top");
  }
  return { ...face, tag, top: t(n - 1), length: L };
}

// A LANDING'S SECTION, continuing a flight's profile: a slab from x0 to x1 (cut every `step`, so a helical map can
// bend it), its top at `top`, `soffit` deep. Its end at x0 is a "joint" -- where the flight it continues stops.
export function slabFace(x0, x1, top, soffit, step = .3) {
  const n = Math.max(1, Math.ceil((x1 - x0) / step)), pts = [], tris = [];
  for (let i = 0; i <= n; i++) { const x = x0 + (x1 - x0) * i / n; pts.push([x, top - soffit], [x, top]); }
  for (let i = 0; i < n; i++) tris.push([2 * i, 2 * i + 2, 2 * i + 3], [2 * i, 2 * i + 3, 2 * i + 1]);
  const face = closeFace(pts, tris), tag = new Map();
  for (const { loop } of face.rings) for (let i = 0; i < loop.length; i++) {
    const a = loop[i], b = loop[(i + 1) % loop.length], [ax, ay] = pts[a], [bx, by] = pts[b];
    tag.set(a < b ? `${a},${b}` : `${b},${a}`, Math.abs(ax - x0) < 1e-9 && Math.abs(bx - x0) < 1e-9 ? "joint-in"
           : Math.abs(ax - x1) < 1e-9 && Math.abs(bx - x1) < 1e-9 ? "joint-out" : Math.abs(ay - top) < 1e-9 && Math.abs(by - top) < 1e-9 ? "top" : "base");
  }
  return { ...face, tag };
}

// the map for a SPIRAL: x round the helix at the walking line `rArc`, the two sides the newel's radius and the
// outer one. A left-handed stair is the right-handed one in a mirror -- and a mirror turns every triangle
// inside out, so the two sides are swapped as well, which turns them back.
export const helix = (rNear, rFar, rArc, hand = 1) => (x, y, side) => {
  const th = hand * x / rArc, r = (side === 0) === (hand > 0) ? rFar : rNear;
  return [r * Math.sin(th), y, r * Math.cos(th)];
};

// ...and a helix whose radius CHANGES as it climbs: `far(x)` and `near(x)` are the edges at distance x along the
// walking line, and the angle is the walking line's own arc length over its radius, summed step by step -- a stair
// between a dome's two shells draws in as the dome does and keeps its treads the same length on the walking line.
// `poly` { n, phase } bends it round a regular polygon instead of a circle -- the gap between an octagonal dome's two
// shells is an octagon: at every angle the radius is the polygon's there (a face's middle nearer, a corner further),
// the polygon's corners at (k + .5) of its sides from `phase`.
export const helixAlong = (near, far, hand = 1, step = .25, poly = null) => {
  const face = poly ? 2 * Math.PI / poly.n : 0;
  // (the offset from the nearest FACE's middle: faces are centred on multiples of `face` from `phase`)
  const k = (t) => { if (!poly) return 1; const off = ((((t + poly.phase + face / 2) % face) + face) % face) - face / 2; return Math.cos(face / 2) / Math.cos(off); };
  const th = [0];
  const thAt = (x) => {
    while ((th.length - 1) * step < x + step) {
      const x0 = (th.length - 1) * step, rw = (near(x0 + step / 2) + far(x0 + step / 2)) / 2;
      th.push(th[th.length - 1] + step / Math.max(.5, rw));
    }
    const i = Math.max(0, Math.floor(x / step)), f = x / step - i;
    return th[i] + (th[Math.min(i + 1, th.length - 1)] - th[i]) * f;
  };
  return (x, y, side) => {
    // (before the start -- a stair's foot -- the helix runs on backward at its first radius)
    const t = hand * (x >= 0 ? thAt(x) : x / Math.max(.5, (near(0) + far(0)) / 2)), f = k(t), outer = (side === 0) === (hand > 0);
    const r = (outer ? far(x) : near(x)) * f;                            // (both edges bend with the polygon: the gap does)
    return [r * Math.sin(t), y, r * Math.cos(t)];
  };
};

// A STAIRCASE OF FLIGHTS AND LANDINGS, as a walk: a flight climbs ahead onto a landing, and from a landing any
// number of flights leave -- ahead, to the left, to the right, or BACK the way it came beside the one that
// arrived. That is the dog-leg, the U, the T and the imperial stair (one flight up the middle to a landing,
// two returning either side of it), and the walk goes on from each of them. Everything is welded into one
// mesh: a flight's joint and the stretch of the landing's edge it lands on are the SAME place, so neither is
// drawn, and the landing's edges are broken where each flight's corners meet them.
//   node: { flight: n risers, width, landing?: { depth, width, shift, then: [ { from: "ahead"|"left"|"right"|
//   "back", at: offset along that edge, ...node } ] } }. A flight's frame has x up the flight and z to its
// right; a landing's `width` is across the arriving flight, `depth` along it, `shift` slides it sideways.
export function staircase(m, root, { run, rise, soffit }) {
  const flights = [], landings = [];
  const walk = (node, ox, oz, dir, h) => {                 // dir: heading as an angle, 0 = +x
    const n = Math.max(1, Math.round(node.flight)), w = node.width;
    const cx = Math.cos(dir), sz = Math.sin(dir);
    const frame = (x, y, z) => [ox + x * cx - z * sz, y, oz + x * sz + z * cx];   // z to the right of the heading
    const f = { n, w, h, frame, top: h + n * rise, length: n * run, landed: !!node.landing };
    flights.push(f);
    const Ld = node.landing;
    if (!Ld) return;
    const depth = Ld.depth, LW = Ld.width ?? w, shift = Ld.shift ?? 0;
    // the landing's own frame: its near edge on the flight's arrival line, x ahead, z to the right
    const L = { h: f.top, frame: (x, z) => frame(f.length + x, f.top, z + shift).filter((_, i) => i !== 1),
                x0: 0, x1: depth, z0: -LW / 2, z1: LW / 2, attach: [] };
    L.attach.push({ edge: "near", a: -w / 2 - shift, b: w / 2 - shift });          // where the flight arrived
    landings.push(L);
    for (const c of Ld.then ?? []) {
      const at = c.at ?? 0, cw = c.width, from = c.from ?? "ahead";
      // where the child starts (in the landing frame), which way it faces, and which edge it leaves from
      const start = from === "ahead" ? [depth, at, 0, "far"] : from === "back" ? [0, at, Math.PI, "near"]
                  : from === "left" ? [at, -LW / 2, -Math.PI / 2, "left"] : [at, LW / 2, Math.PI / 2, "right"];
      const [lx, lz, turn, edge] = start;
      const along = edge === "near" || edge === "far" ? lz : lx;
      L.attach.push({ edge, a: along - cw / 2, b: along + cw / 2 });
      const [wx, , wz] = frame(f.length + lx, 0, lz + shift);
      walk({ ...c, _from: edge }, wx, wz, dir + turn, f.top);
    }
  };
  walk(root, 0, 0, 0, 0);
  // the WALKING PATH, for the clearance check: every tread's middle, every landing's
  const path = [];
  for (const f of flights) {
    for (let k = 0; k < f.n; k++) path.push({ p: f.frame((k + .5) * run, f.h + (k + 1) * rise, 0), w: f.w });
    f.foot = f.frame(-.5, f.h, 0);
  }
  for (const L of landings) { const [X, Z] = L.frame((L.x0 + L.x1) / 2, (L.z0 + L.z1) / 2); path.push({ p: [X, L.h, Z], w: Math.min(L.x1 - L.x0, L.z1 - L.z0), landing: true }); }
  // THE LANDINGS' FREE EDGES -- every stretch of a landing's outline no flight arrives at or leaves from -- each with
  // the way out of the landing across it: where the railing may run (assemble.js railingsFor asks whether it is open)
  const edgesFree = [];
  for (const L of landings) {
    const sides = { near: [[L.x0, L.z1], [L.x0, L.z0], [-1, 0]], left: [[L.x0, L.z0], [L.x1, L.z0], [0, -1]],
                    far: [[L.x1, L.z0], [L.x1, L.z1], [1, 0]], right: [[L.x1, L.z1], [L.x0, L.z1], [0, 1]] };
    for (const [e, [[x0, z0], [x1, z1], [nx, nz]]] of Object.entries(sides)) {
      const along = (x, z) => (e === "near" || e === "far" ? z : x), c0 = along(x0, z0), c1 = along(x1, z1);
      const lo = Math.min(c0, c1), hi = Math.max(c0, c1);
      const taken = L.attach.filter((q) => q.edge === e).map((q) => [Math.max(lo, Math.min(q.a, q.b)), Math.min(hi, Math.max(q.a, q.b))]).sort((a, b) => a[0] - b[0]);
      let c = lo;
      const free = [];
      for (const [a, b] of taken) { if (a > c + 1e-6) free.push([c, a]); c = Math.max(c, b); }
      if (hi > c + 1e-6) free.push([c, hi]);
      const at = (t) => (e === "near" || e === "far" ? [x0, t] : [t, z0]);
      // (in the order and the direction the outline runs, so a free stretch that turns a corner is one railing)
      const run = c1 >= c0 ? free : free.reverse().map(([a, b]) => [b, a]);
      for (const [a, b] of run) {
        const [ax, az] = at(a), [bx, bz] = at(b), A = L.frame(ax, az), B = L.frame(bx, bz), O = L.frame(ax + nx, az + nz);
        edgesFree.push({ a: [A[0], L.h, A[1]], b: [B[0], L.h, B[1]], n: [O[0] - A[0], O[1] - A[1]] });
      }
    }
  }
  // THE FLIGHTS: each its profile swept across its width, the joints left out where a landing meets them
  for (const f of flights) {
    const face = flightFace(f.n, run, rise, soffit, f.h, true);
    const skip = new Set();
    if (f.landed) skip.add("joint-out");                   // (the last flight's end stands against the floor it reaches)
    if (f.h > 1e-9) skip.add("joint-in");                  // one that starts on the ground shows its foot
    const walls = ["top", "base", "joint-in", "joint-out"].filter((v) => !skip.has(v));
    const map = (x, y, side) => f.frame(x, y, side ? -f.w / 2 : f.w / 2);   // the face's front is its right side
    extrude(face, map, m, { caps: true, walls });
  }
  // THE LANDINGS: slabs `soffit` deep, their outline broken at every flight's corner, fanned from the middle
  for (const L of landings) {
    const edges = {                                         // each edge as [from, to] in the landing frame, CCW from above
      near: [[L.x0, L.z1], [L.x0, L.z0]], left: [[L.x0, L.z0], [L.x1, L.z0]],
      far: [[L.x1, L.z0], [L.x1, L.z1]], right: [[L.x1, L.z1], [L.x0, L.z1]] };
    const ring = [];                                        // [x, z, attached-after]
    for (const e of ["near", "left", "far", "right"]) {
      const [[x0, z0], [x1, z1]] = edges[e];
      const coord = (x, z) => (e === "near" || e === "far" ? z : x);          // position along the edge
      const c0 = coord(x0, z0), c1 = coord(x1, z1);
      const cuts = new Set([c0]);
      const spans = L.attach.filter((q) => q.edge === e).sort((p, q) => p.a - q.a);
      for (let i = 1; i < spans.length; i++) if (spans[i].a < spans[i - 1].b - 1e-9)
        throw new Error(`two flights overlap on the landing's ${e} edge -- move one along it with "at"`);
      for (const q of spans) {
        if (Math.min(q.a, q.b) < Math.min(c0, c1) - 1e-9 || Math.max(q.a, q.b) > Math.max(c0, c1) + 1e-9)
          throw new Error(`a flight ${(q.b - q.a).toFixed(2)}m wide does not fit on the landing's ${e} edge`);
        cuts.add(q.a); cuts.add(q.b);
      }
      const list = [...cuts].filter((c) => Math.abs(c - c1) > 1e-9).sort((p, q) => (c1 > c0 ? p - q : q - p));
      for (const c of list) {
        const x = e === "near" || e === "far" ? x0 : c, z = e === "near" || e === "far" ? c : z0;
        const next = list[list.indexOf(c) + 1] ?? c1, mid = (c + next) / 2;
        const covered = spans.some((q) => mid > Math.min(q.a, q.b) + 1e-9 && mid < Math.max(q.a, q.b) - 1e-9);
        ring.push([x, z, covered]);
      }
    }
    const top = ring.map(([x, z]) => { const [X, Z] = L.frame(x, z); return m.vert(X, L.h, Z); });
    const bot = ring.map(([x, z]) => { const [X, Z] = L.frame(x, z); return m.vert(X, L.h - soffit, Z); });
    const [cX, cZ] = L.frame((L.x0 + L.x1) / 2, (L.z0 + L.z1) / 2);
    const cT = m.vert(cX, L.h, cZ), cB = m.vert(cX, L.h - soffit, cZ);
    for (let i = 0; i < ring.length; i++) {
      const j = (i + 1) % ring.length;
      m.tri(cT, top[j], top[i]);                            // (the ring runs clockwise seen from above, so these face up)
      m.tri(cB, bot[i], bot[j]);
      if (!ring[i][2]) m.quad(top[i], top[j], bot[j], bot[i]);
    }
  }
  // THE TOP LANDINGS -- those no flight leaves -- each by its far edge and the way on across it: where the floor the
  // stair arrives on begins (assemble.js arrivalFloor)
  const tops = landings.filter((L) => L.attach.length === 1).map((L) => {
    const [ax, az] = L.frame(L.x1, L.z0), [bx, bz] = L.frame(L.x1, L.z1), [ox, oz] = L.frame(L.x1 + 1, L.z0);
    return { a: [ax, L.h, az], b: [bx, L.h, bz], out: [ox - ax, oz - az] };
  });
  return { m, flights, landings, path, edges: edgesFree, tops };
}

// ---- coffers ----------------------------------------------------------------------------------------------
// COFFERS ARE CUT INTO A SURFACE, not laid on it: a grid of cells, each a frame left at the surface and a
// pocket sunk behind it in `steps` stepped rings, the Pantheon's five rows of twenty-eight. So they are written
// over any surface given as S(u, v) -- a flat ceiling, a dome's soffit -- with N(u, v) the direction INTO the
// stone (where the pockets go). u and v are in the surface's own station units: a cell is `ku` stations wide and
// `kv` high, and the cell's edges carry every station on them, so the surface round the coffered field (the
// dome's plain rings above and below) meets it point for point. `frame` is the frame's share of the cell on each
// side, `step` how much further each step comes in, `depth` how deep the last one is.
export function cofferedSurface(m, S, N, { nu, nv, ku = 1, kv = 1, frame = .12, step = .06, steps = 1, depth }) {
  const at = (u, v, off) => { const p = S(u, v); if (!off) return p; const n = N(u, v); return [p[0] + n[0] * off, p[1] + n[1] * off, p[2] + n[2] * off]; };
  const V = (u, v, off = 0) => m.vert(...at(u, v, off));
  // which way round a polygon drawn counter-clockwise in (u, v) faces: toward the room, or into the stone
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const c0 = at(nu * ku / 2, nv * kv / 2), cu = sub(at(nu * ku / 2 + .01, nv * kv / 2), c0), cv = sub(at(nu * ku / 2, nv * kv / 2 + .01), c0);
  const cr = [cu[1] * cv[2] - cu[2] * cv[1], cu[2] * cv[0] - cu[0] * cv[2], cu[0] * cv[1] - cu[1] * cv[0]], n0 = N(nu * ku / 2, nv * kv / 2);
  const ccw = cr[0] * n0[0] + cr[1] * n0[1] + cr[2] * n0[2] < 0;          // (u, v) counter-clockwise faces the room
  const tri = (a, b, c) => ccw ? m.tri(a, b, c) : m.tri(a, c, b);
  const quad = (a, b, c, d) => { tri(a, b, c); tri(a, c, d); };
  for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) {
    const u0 = i * ku, u1 = u0 + ku, v0 = j * kv, v1 = v0 + kv;
    // the cell's outline, counter-clockwise, side by side, every station on it
    const side = [
      Array.from({ length: ku + 1 }, (_, k) => [u0 + k, v0]),
      Array.from({ length: kv + 1 }, (_, k) => [u1, v0 + k]),
      Array.from({ length: ku + 1 }, (_, k) => [u1 - k, v1]),
      Array.from({ length: kv + 1 }, (_, k) => [u0, v1 - k]),
    ];
    const rect = (f) => [[u0 + f * ku, v0 + f * kv], [u1 - f * ku, v0 + f * kv], [u1 - f * ku, v1 - f * kv], [u0 + f * ku, v1 - f * kv]];
    // the frame: four strips from the outline in to the first ring, at the surface
    const r0 = rect(frame).map(([u, v]) => V(u, v));
    for (let e = 0; e < 4; e++) {
      const outer = side[e].map(([u, v]) => V(u, v)), a = r0[e], b = r0[(e + 1) % 4];
      for (let k = 0; k + 1 < outer.length; k++) tri(a, outer[k], outer[k + 1]);
      tri(a, outer[outer.length - 1], b);
    }
    // the pocket: down a step, in along a ledge, down again ... to the bottom
    for (let L = 0; L < steps; L++) {
      const f = frame + L * step, dA = depth * L / steps, dB = depth * (L + 1) / steps;
      const top = rect(f).map(([u, v]) => V(u, v, dA)), bot = rect(f).map(([u, v]) => V(u, v, dB));
      for (let e = 0; e < 4; e++) quad(top[e], top[(e + 1) % 4], bot[(e + 1) % 4], bot[e]);
      if (L + 1 < steps) {
        const inn = rect(f + step).map(([u, v]) => V(u, v, dB));
        for (let e = 0; e < 4; e++) quad(bot[e], bot[(e + 1) % 4], inn[(e + 1) % 4], inn[e]);
      } else quad(bot[0], bot[1], bot[2], bot[3]);
    }
  }
  return m;
}

// A DRUM, closed: `sides` flat faces from radius r0 at y0 to r1 at y1 -- a pier, a shaft with its taper, a
// newel, a column's base, the flare of a capital. (Wound outward: the ring runs from +x toward +z, which seen
// from above is clockwise.)
export function drum(m, r0, r1, y0, y1, sides) {
  const ring = (r, y) => Array.from({ length: sides }, (_, k) => { const t = k * 2 * Math.PI / sides; return m.vert(r * Math.cos(t), y, r * Math.sin(t)); });
  const lo = ring(r0, y0), hi = ring(r1, y1);
  for (let k = 0; k < sides; k++) m.quad(lo[k], hi[k], hi[(k + 1) % sides], lo[(k + 1) % sides]);
  const cLo = m.vert(0, y0, 0), cHi = m.vert(0, y1, 0);
  for (let k = 0; k < sides; k++) { m.tri(cLo, lo[k], lo[(k + 1) % sides]); m.tri(cHi, hi[(k + 1) % sides], hi[k]); }
  return m;
}

// A TURNED SOLID: the profile [[r, y], ...] (bottom to top) revolved round the y axis in `sides`, capped at both ends --
// a bell capital, a baluster: one closed surface, no rings stacked on rings
export function lathe(m, prof, sides) {
  const rings = prof.map(([r, y]) => Array.from({ length: sides }, (_, k) => { const t = k * 2 * Math.PI / sides; return m.vert(r * Math.cos(t), y, r * Math.sin(t)); }));
  for (let j = 0; j + 1 < rings.length; j++) for (let k = 0; k < sides; k++) m.quad(rings[j][k], rings[j + 1][k], rings[j + 1][(k + 1) % sides], rings[j][(k + 1) % sides]);
  const lo = rings[0], hi = rings[rings.length - 1], cLo = m.vert(0, prof[0][1], 0), cHi = m.vert(0, prof[prof.length - 1][1], 0);
  for (let k = 0; k < sides; k++) { m.tri(cLo, lo[k], lo[(k + 1) % sides]); m.tri(cHi, hi[(k + 1) % sides], hi[k]); }
  return m;
}

// ---- plans: polygons on the ground ----------------------------------------------------------------------------
// THE OUTLINE OF A BUILDING, as points on the ground (x, z), counter-clockwise seen from above (so the outside of
// every edge is on its right as you walk it): a rectangle `rect: [w, l]`, the same with its corners cut off
// (`chamfer`: the Taj Mahal's, the Frauenkirche's), a regular polygon (`sides`, `radius` to its corners, turned
// so a flat face looks toward +z as a ring's bay does), or the points themselves.
//   Every edge carries a LABEL -- "side" for a rectangle or a polygon, "main" and "chamfer" for a chamfered
// rectangle -- and `split: { <label>: [lengths] }` divides every edge of that label into segments of those
// lengths (weights, scaled to the edge), labelled "<label>:0", "<label>:1"...: a facade that is a flank, a centre
// bay and a flank, each a face of its own. The points come back with `labels`, one per edge.
export function planPoints(plan) {
  let pts, labels;
  if (plan.points) { pts = plan.points.map(([x, z]) => [x, z]); labels = pts.map(() => "side"); }
  else if (plan.sides) {
    const n = Math.max(3, Math.round(plan.sides)), r = plan.radius;
    pts = Array.from({ length: n }, (_, k) => { const t = (k + .5) * 2 * Math.PI / n; return [r * Math.sin(t), r * Math.cos(t)]; });
    labels = pts.map(() => "side");
  } else {
    const [w, l] = plan.rect, c = Math.min(plan.chamfer ?? 0, w / 2 - 1e-6, l / 2 - 1e-6), a = w / 2, b = l / 2;
    pts = c > 0 ? [[-a + c, -b], [a - c, -b], [a, -b + c], [a, b - c], [a - c, b], [-a + c, b], [-a, b - c], [-a, -b + c]]
                : [[-a, -b], [a, -b], [a, b], [-a, b]];
    labels = pts.map((_, i) => (c > 0 ? (i % 2 ? "chamfer" : "main") : "side"));
  }
  let area = 0;
  for (let i = 0; i < pts.length; i++) { const [x0, z0] = pts[i], [x1, z1] = pts[(i + 1) % pts.length]; area += x0 * z1 - x1 * z0; }
  if (area > 0) {                                  // this winding has the outside on the right of every edge
    pts = pts.reverse();
    labels = labels.reverse();                     // (edge i ran p[i] -> p[i+1]; reversed, it is the edge ending there)
    labels = [...labels.slice(1), labels[0]];
  }
  if (plan.split) {
    const P2 = [], L2 = [];
    for (let i = 0; i < pts.length; i++) {
      const p0 = pts[i], p1 = pts[(i + 1) % pts.length], parts = plan.split[labels[i]];
      P2.push(p0);
      if (!parts) { L2.push(labels[i]); continue; }
      const total = parts.reduce((x, y) => x + y, 0);
      let acc = 0;
      parts.forEach((len, k) => {
        L2.push(`${labels[i]}:${k}`);
        acc += len;
        if (k + 1 < parts.length) { const f = acc / total; P2.push([p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f]); }
      });
    }
    pts = P2; labels = L2;
  }
  pts.labels = labels;
  return pts;
}

// the same outline moved IN by `t` on every side, its corners mitred: the inner face of a wall round it
export function insetPoints(pts, t) {
  const n = pts.length, out = [];
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i + n - 1) % n], p1 = pts[i], p2 = pts[(i + 1) % n];
    const e0 = [p1[0] - p0[0], p1[1] - p0[1]], e1 = [p2[0] - p1[0], p2[1] - p1[1]];
    const l0 = Math.hypot(...e0), l1 = Math.hypot(...e1);
    // inward normals: the outside is on the right of each edge, so the inside is on its left
    const n0 = [e0[1] / l0, -e0[0] / l0], n1 = [e1[1] / l1, -e1[0] / l1];
    const bis = [n0[0] + n1[0], n0[1] + n1[1]], k = t / (1 + n0[0] * n1[0] + n0[1] * n1[1]);
    out.push([p1[0] + bis[0] * k, p1[1] + bis[1] * k]);
  }
  return out;
}

// A STACK OF OUTLINES, closed: each level the same number of points (planPoints' winding) at a height, joined to
// the next side by side -- a stepped platform is its steps' outlines at their feet and their treads. The
// bottom and the top are fanned from their middles.
export function stackMesh(m, levels) {
  const rings = levels.map(({ pts, y }) => pts.map(([x, z]) => m.vert(x, y, z))), n = levels[0].pts.length;
  for (let i = 0; i + 1 < rings.length; i++) for (let k = 0; k < n; k++) {
    const k2 = (k + 1) % n, a = rings[i], b = rings[i + 1];
    m.quad(a[k], a[k2], b[k2], b[k]);
  }
  const mid = (L) => [L.pts.reduce((s2, p) => s2 + p[0], 0) / n, L.y, L.pts.reduce((s2, p) => s2 + p[1], 0) / n];
  const lo = levels[0], hi = levels[levels.length - 1], cLo = m.vert(...mid(lo)), cHi = m.vert(...mid(hi));
  for (let k = 0; k < n; k++) {
    const k2 = (k + 1) % n;
    m.tri(cLo, rings[0][k2], rings[0][k]);
    m.tri(cHi, rings[rings.length - 1][k], rings[rings.length - 1][k2]);
  }
  return m;
}

// A PRISM: the outline carried from y0 up to y1, closed -- a plinth, a platform, a mass, a tower's core.
// Its top and bottom are fanned from the middle (the outlines are convex).
// `y1` may be a function of (x, z): a top that is not level (a prism's `slope`), its sides cut off under it
export function prismMesh(m, pts, y0, y1, well = null) {
  const top = typeof y1 === "function" ? y1 : () => y1;
  // (with a well, the outline takes a corner where the line its caps are cut on crosses it: the sides meet the caps there)
  if (well) pts = pts.flatMap((a, i) => { const b = pts[(i + 1) % pts.length], da = a[0] - well.cx, db = b[0] - well.cx;
    return da * db < -1e-12 ? [a, [well.cx, a[1] + (b[1] - a[1]) * da / (da - db)]] : [a]; });
  const lo = pts.map(([x, z]) => m.vert(x, y0, z)), hi = pts.map(([x, z]) => m.vert(x, top(x, z), z)), n = pts.length;
  for (let k = 0; k < n; k++) {
    const k2 = (k + 1) % n;
    m.quad(lo[k], lo[k2], hi[k2], hi[k]);             // (planPoints' winding: the outside on the right)
  }
  // the caps ear-clipped, so a plan need not be convex (a floor round a half ring is a U); earClip hands its
  // triangles back counter-clockwise in (x, z), which faces down
  const caps = (q) => {
    const l = q.map(([x, z]) => m.vert(x, y0, z)), h = q.map(([x, z]) => m.vert(x, top(x, z), z));
    for (const [a, b, c] of earClip(q, q.map((_, i) => i))) { m.tri(l[a], l[b], l[c]); m.tri(h[a], h[c], h[b]); }
  };
  if (!well) { caps(pts); return m; }
  // A WELL through it -- the hole a stair comes up through (wellPoints: a ring of points from its top, (cx, cz + r),
  // round by +x to its foot and back by -x). Its sides face into it; its caps are the plan cut in two down the line
  // through the well's middle, each half the outline's own side carried round the well's half on that side.
  const { pts: W, cx } = well, N = W.length, on = (q) => Math.abs(q[0] - cx) < 1e-6;
  for (let k = 0; k < N; k++) { const k2 = (k + 1) % N, a = W[k], b = W[k2];
    m.quad(m.vert(b[0], y0, b[1]), m.vert(a[0], y0, a[1]), m.vert(a[0], top(a[0], a[1]), a[1]), m.vert(b[0], top(b[0], b[1]), b[1])); }
  const half = N / 2;
  for (const sd of [1, -1]) {
    // the outline clipped to this side of the line (Sutherland-Hodgman, one plane)
    const c = [];
    for (let i = 0; i < n; i++) {
      const a = pts[i], b = pts[(i + 1) % n], da = sd * (a[0] - cx), db = sd * (b[0] - cx);
      if (da >= -1e-9) c.push(a);
      if ((da > 1e-9 && db < -1e-9) || (da < -1e-9 && db > 1e-9)) { const t = da / (da - db); c.push([cx, a[1] + (b[1] - a[1]) * t]); }
    }
    const i = c.findIndex((q, j) => on(q) && on(c[(j + 1) % c.length]));
    if (i < 0) continue;
    // round the outline from the far end of the cut to its near end, then down the cut into the well and round its
    // half on this side
    const chain = [...c.slice(i + 1), ...c.slice(0, i + 1)], end = chain[chain.length - 1];
    const ring = sd > 0 ? W.slice(0, half + 1) : [...W.slice(half), W[0]];
    const arc = (end[1] > chain[0][1]) === (ring[0][1] > ring[ring.length - 1][1]) ? ring : ring.slice().reverse();
    caps([...chain, ...arc]);
  }
  return m;
}
// the WELL's outline for prismMesh: `radius` round (an even `sides`, 16 by default) or `rect` [w, l], about `at`
export function wellPoints(w) {
  const [cx, cz] = w.at ?? [0, 0];
  if (w.rect) { const a = w.rect[0] / 2, b = w.rect[1] / 2; return { cx, pts: [[cx, cz + b], [cx + a, cz + b], [cx + a, cz - b], [cx, cz - b], [cx - a, cz - b], [cx - a, cz + b]] }; }
  // (`turn`: its corners that many sides round -- .5 sets them as a polygon plan's, a flat face across each axis)
  const N = 2 * Math.max(2, Math.round((w.sides ?? 16) / 2)), r = w.radius, t = w.turn ?? 0;
  return { cx, pts: Array.from({ length: N }, (_, k) => [cx + r * Math.sin((k + t) * 2 * Math.PI / N), cz + r * Math.cos((k + t) * 2 * Math.PI / N)]) };
}

// GLASS IN THE WINDOWS: every GLAZED opening of a face gets a pane of its own exact outline -- its foot or sill,
// its jambs, its head -- set in the middle of the wall's thickness, halfway between where `map` puts the face's
// front and its back. An opening is glazed as its definition says (`glass`, assemble.js glassOf); said nowhere,
// one standing over the floor (a sill over 30cm) is, and a door or an arcade is left open.
//   A window with `tracery` has its stone bars too (tracery.js), built into `g.tracery` -- a mesh of their own, stone
// beside the glass: the part that takes the glass takes them as a part of their own. An open window -- a belfry's,
// an openwork stage's -- may have tracery and no glass.
// (`height`: what the wall it is part of rises to over the face's foot -- a wimperg stands within it)
export function glassPanes(face, map, g, height = face.h) {
  const mid = (x, y) => { const a = map(x, y, 0), b = map(x, y, 1); return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2]; };
  // (the dressed openings of the row, counted from its middle: which pediment an alternating row gives each)
  // (a LOMBARD BAND over the face, its lesenes and arched corbel table: lombard.js)
  if (face.lombard) lombardMesh(face, face.lombard, map, g.surround ??= mesh(), height);
  const dressed = (face.openings ?? []).filter((o) => o.surround);
  // (and the free wall each side of each: to the face's end, or half the pier it shares with the next opening)
  const ops = [...(face.openings ?? [])].sort((p, q) => p.x0 - q.x0);
  const room = (o) => { const i = ops.indexOf(o), l = ops[i - 1], r = ops[i + 1];
                        return [l ? (o.x0 - l.x1) / 2 : o.x0, r ? (r.x0 - o.x1) / 2 : (face.w ?? Infinity) - o.x1]; };
  for (const o of face.openings ?? []) {
    // (a WIMPERG over it, glazed or not -- a portal carries one as well as a window: wimperg.js; or a classical
    //  SURROUND: surround.js)
    if (o.wimperg) wimpergMesh(o, o.wimperg, map, g.wimperg ??= mesh(), height);
    if (o.surround) surroundMesh({ ...o, room: room(o), turn: Math.round(Math.abs(dressed.indexOf(o) - (dressed.length - 1) / 2)) }, o.surround, map, g.surround ??= mesh(), height);
    if (!(o.glass ?? o.sill > .3)) { if (o.tracery && o.sill > .3) traceryMesh(o, o.tracery, map, g.tracery ??= mesh()); continue; }
    const bottom = o.foot ? o.foot.map(([fx, fy]) => [o.at + fx, o.sill + fy]) : [[o.j0, o.sill], [o.j1, o.sill]];
    const top = o.curve.map(([cx, cy]) => [o.at + cx, o.springing + cy]).reverse();
    const raw = [...bottom, ...top], pts = [];
    for (const q of raw) { const l = pts[pts.length - 1]; if (!l || Math.hypot(q[0] - l[0], q[1] - l[1]) > 1e-6) pts.push(q); }
    if (pts.length > 2 && Math.hypot(pts[0][0] - pts[pts.length - 1][0], pts[0][1] - pts[pts.length - 1][1]) < 1e-6) pts.pop();
    if (pts.length < 3) continue;
    const ids = pts.map(([x, y]) => g.vert(...mid(x, y)));
    for (const [a, b, c] of earClip(pts, pts.map((_, i) => i))) g.tri(ids[a], ids[b], ids[c]);
    if (o.tracery) traceryMesh(o, o.tracery, map, g.tracery ??= mesh());
  }
  return g;
}

// A FACE IN TIERS: one wall face `L` long made of horizontal bands stacked -- `tiers` is [{ h, openings }], lowest
// first -- so a window can stand over a door and a row of windows over another (the strip triangulation of
// wallFace cannot put two openings in one column). Each band is its own face, extruded by `mapAt(y0)`; where two
// meet, the joint is inside the stone and is not drawn, and it is one edge on both sides (a band's top and
// bottom are cut only at its corners, so long as no opening touches them). `ends` tags the face's two end
// verticals too, for a wall whose ends are mitres shared with its neighbour ([start, end] for one of them).
export function tieredWall(m, L, tiers, mapAt, { ends = false, endCuts = [], glass = null } = {}) {
  // (`ends` may be [start, end]: a wall along an open line meets a neighbour at its inner joints only)
  const [end0, end1] = Array.isArray(ends) ? ends : [ends, ends];
  // where each band's openings stand: a joint carries both bands' jambs, so the two edges are one
  const faces0 = tiers.map((tier) => wallFace(L, tier.h, tier.openings ?? []).openings);
  const jambs = faces0.map((os) => os.flatMap((o) => [o.x0, o.x1]));
  // a DOOR in a band above (an opening from its very foot) stands on the band below: that band's top is its
  // threshold there, drawn, not a joint hidden in the stone
  const doors = faces0.map((os) => os.filter((o) => o.sill < 1e-6).map((o) => [o.x0, o.x1]));
  const under = (k, ax, bx) => (doors[k + 1] ?? []).some(([x0, x1]) => (ax + bx) / 2 > x0 + 1e-9 && (ax + bx) / 2 < x1 - 1e-9);
  let y0 = 0;
  tiers.forEach((tier, k) => {
    const joint = (j) => (j >= 0 && j < tiers.length ? [...jambs[j], ...jambs[k]] : []);
    const face = wallFace(L, tier.h, tier.openings ?? [], { topCuts: joint(k + 1), bottomCuts: joint(k - 1),
                                                           endCuts: endCuts.map((v) => v - y0) });
    face.tag = new Map();
    if (tier.lombard) face.lombard = tier.lombard;
    const mark = (a, b, v) => face.tag.set(a < b ? `${a},${b}` : `${b},${a}`, v);
    for (const { loop } of face.rings) for (let i = 0; i < loop.length; i++) {
      const a = loop[i], b = loop[(i + 1) % loop.length], [ax, ay] = face.pts[a], [bx, by] = face.pts[b];
      if ((end0 && Math.abs(ax) < 1e-9 && Math.abs(bx) < 1e-9) || (end1 && Math.abs(ax - L) < 1e-9 && Math.abs(bx - L) < 1e-9)) mark(a, b, "joint");
      if (k > 0 && Math.abs(ay) < 1e-9 && Math.abs(by) < 1e-9) mark(a, b, "joint");                    // sits on the tier below
      if (k + 1 < tiers.length && Math.abs(ay - tier.h) < 1e-9 && Math.abs(by - tier.h) < 1e-9 && !under(k, ax, bx)) mark(a, b, "joint");
    }
    extrude(face, mapAt(y0), m, { caps: true, walls: ["wall"] });
    // (what dresses its openings stays under the wall's top -- or the tier's own `top`, an entablature over it)
    if (glass) glassPanes(face, mapAt(y0), glass, tier.top ?? tiers.reduce((t, b) => t + b.h, 0) - y0);
    y0 += tier.h;
  });
  return m;
}

// WALLS ROUND A PLAN: each edge of the outline is a wall face (in tiers, if it has them) extruded from the
// outline in to the same outline moved in by `t` -- so two faces meet on their mitre exactly, and the ring of
// them closes as a ring of bays does. The face's x runs along the edge from its first corner; its two ends are
// the mitre shared with the next face and are not drawn. `faces[i]` is that edge's tiers, openings laid out.
export function enclosureMesh(m, pts, t, faces, glass = null) {
  const inner = insetPoints(pts, t), n = pts.length, along = innerAlong(pts, t, faces);
  // every joint between tiers, on any face: the corners carry them all, so faces with different tiers still meet
  const joints = [...new Set(faces.flatMap((tiers) => { let y = 0; return tiers.slice(0, -1).map((b) => (y += b.h)); }))];
  for (let i = 0; i < n; i++) {
    const P0 = pts[i], P1 = pts[(i + 1) % n], Q0 = inner[i], Q1 = inner[(i + 1) % n], { L, Li, u } = along[i];
    const mapAt = (y0) => (x, y, side) => {
      const f = side ? u(x) / Li : x / L, A = side ? Q0 : P0, B = side ? Q1 : P1;
      return [A[0] + (B[0] - A[0]) * f, y0 + y, A[1] + (B[1] - A[1]) * f];
    };
    tieredWall(m, L, faces[i], mapAt, { ends: true, endCuts: joints, glass });
  }
  return m;
}

// WHERE A POINT OF AN ENCLOSURE'S OUTER FACE COMES THROUGH ON ITS INNER ONE: per face { L, Li, u }, u(x) the distance
// along the inner face (from its first corner) of the point x along the outer.
// SQUARE REVEALS: the inner face is shorter than the outer by the mitres, and mapping the one onto the other in
// proportion skews every opening through the wall. So the inner face runs PARALLEL through the middle -- from the
// first opening to the last -- and takes up the difference only in the stretches at its two ends.
export function innerAlong(pts, t, faces) {
  const inner = insetPoints(pts, t), n = pts.length;
  return pts.map((P0, i) => {
    const P1 = pts[(i + 1) % n], Q0 = inner[i], Q1 = inner[(i + 1) % n];
    const L = Math.hypot(P1[0] - P0[0], P1[1] - P0[1]), Li = Math.hypot(Q1[0] - Q0[0], Q1[1] - Q0[1]);
    const ex = [(P1[0] - P0[0]) / L, (P1[1] - P0[1]) / L], d0 = (Q0[0] - P0[0]) * ex[0] + (Q0[1] - P0[1]) * ex[1];
    const xs = faces[i].flatMap((t) => t.openings.flatMap((o) => [o.at - o.width / 2, o.at + o.width / 2]));
    const e1 = Math.min(...xs, L / 2), e2 = Math.max(...xs, L / 2);
    const par = e1 - d0 > 1e-6 && Li - e2 + d0 > 1e-6;          // (the openings stand clear of the mitres)
    const u = (x) => !par ? x * Li / L
      : x <= e1 ? x * (e1 - d0) / e1                              // the stretch at the start, taking up the mitre
      : x >= e2 ? (e2 - d0) + (x - e2) * (Li - e2 + d0) / (L - e2) // ...and at the end
      : x - d0;                                                   // parallel through the middle
    return { L, Li, u };
  });
}

// A FLYING BUTTRESS: a strut on a rampant arch, from a buttress pier (x 0) across `span` to the wall it props.
// Its underside is a quarter ellipse -- rising vertically off the pier at `low`, arriving level at the wall at
// `high` -- and its top runs straight from `top0` over the pier to `top1` at the wall. The face is that outline,
// extruded `width` thick, centred.
export function flyerMesh(m, { span, low, high, top0, top1, width, per90 = 4 }) {
  const n = Math.max(2, Math.round(per90));
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const t = (i / n) * Math.PI / 2;
    pts.push([span - span * Math.cos(t), low + (high - low) * Math.sin(t)]);
  }
  pts.push([span, top1], [0, top0]);
  const face = closeFace(pts, earClip(pts, pts.map((_, i) => i)));
  return extrude(face, (x, y, side) => [x, y, width / 2 - side * width], m);
}

// A BOX, closed: plinths, podiums, the courses of a stylobate, an entablature's straight run.
export function box(m, x0, x1, y0, y1, z0, z1) {
  const c = [[x0, z0], [x1, z0], [x1, z1], [x0, z1]];
  const lo = c.map(([x, z]) => m.vert(x, y0, z)), hi = c.map(([x, z]) => m.vert(x, y1, z));
  m.quad(lo[0], lo[1], lo[2], lo[3]);                                   // (seen from above the ring runs clockwise)
  m.quad(hi[3], hi[2], hi[1], hi[0]);
  for (let k = 0; k < 4; k++) m.quad(lo[(k + 1) % 4], lo[k], hi[k], hi[(k + 1) % 4]);
  return m;
}

// ---- roofs -------------------------------------------------------------------------------------------------
// EVERY COMMON ROOF IS A STACK OF RECTANGLES. The eave is one; a ridge is a rectangle of no width; a hip's
// ridge is one shorter than the eave by the hips; a mansard's break line is one inset all round, a gambrel's
// inset on the long sides only. Join each level to the next, side by side, and a side that is inset between
// two levels is a SLOPE while a side that is not is a vertical -- a GABLE. So a form is nothing but the list
// of its levels, and one function builds them all: a level of zero width welds its corners into a ridge, one
// of zero size into an apex, and the faces that collapse are dropped by the mesh's own weld.
//   A level is { x0, x1, z0, z1, y }. The ridge runs along z. The solid is closed: a soffit under the eave
// and, if the last level still has an area (a flat-topped mansard, a flat roof), a lid over it.
// `inner`: a SHELL roof -- the stack its underside follows (the same levels without the verge, lowered by the covering's
// thickness): its slopes face down into the roof space, and a band all round the eave joins it to the outer stack, so the
// roof is a closed skin over an open space (an attic, a loft) instead of solid down to a soffit at its eaves.
// `open`: the GABLE ends left open -- "front" (+z), "back" (-z) or "ends" (both): a ridge tent's doorway, an open shed.
// Only a vertical side (a gable) is left out; a slope is always drawn. (A shell roof's: its inner face goes with it,
// and the covering's thickness shows there instead -- a strip up each verge from the outer slope to the inner, the
// eave band left off that side -- so the sheet is still closed, cut off square at the doorway.)
export function roofMesh(m, levels, inner = null, open = null) {
  // (a level with a CHAMFER `c` is an octagon -- its corners cut at 45 degrees, `c` along each side: a roof over a
  //  chamfered plan, its corners hipped down onto the chamfers; then every level is, the chamfer 0 where it has run out,
  //  so the rings match corner for corner and the sides between them close)
  const oct = levels.some((L) => L.c > 0) || inner?.some((L) => L.c > 0), N = oct ? 8 : 4, S = N / 4;
  const ring = (L) => {
    const c = Math.max(0, Math.min(L.c ?? 0, (L.x1 - L.x0) / 2, (L.z1 - L.z0) / 2));
    const q = oct ? [[L.x0 + c, L.z0], [L.x1 - c, L.z0], [L.x1, L.z0 + c], [L.x1, L.z1 - c], [L.x1 - c, L.z1], [L.x0 + c, L.z1], [L.x0, L.z1 - c], [L.x0, L.z0 + c]]
                  : [[L.x0, L.z0], [L.x1, L.z0], [L.x1, L.z1], [L.x0, L.z1]];
    return q.map(([x, z]) => m.vert(x, L.y, z));
  };
  const fan = (r, up) => { for (let k = 1; k + 1 < N; k++) up ? m.tri(r[0], r[k + 1], r[k]) : m.tri(r[0], r[k], r[k + 1]); };
  const rings = levels.map(ring);
  const ends = (open === "ends" ? [0, 2] : open === "front" ? [2] : open === "back" ? [0] : []).map((k) => k * S);   // (side 0 runs along z0, side 2 along z1)
  const gableOpen = (Ls, i, k) => ends.includes(k) && Math.abs(k === 0 ? Ls[i].z0 - Ls[i + 1].z0 : Ls[i].z1 - Ls[i + 1].z1) < 1e-9;
  for (let i = 0; i + 1 < rings.length; i++) for (let k = 0; k < N; k++) {
    const a = rings[i], b = rings[i + 1], k2 = (k + 1) % N;
    if (gableOpen(levels, i, k)) continue;
    m.quad(a[k2], a[k], b[k], b[k2]);                                  // outward: each side's slope, or its gable
  }
  const lo = rings[0], hi = rings[rings.length - 1];
  fan(hi, true);                                                        // (a ridge or an apex welds this away)
  if (!inner) { fan(lo, false); return m; }                             // the soffit, facing down
  const inn = inner.map(ring);
  for (let i = 0; i + 1 < inn.length; i++) for (let k = 0; k < N; k++) {
    const a = inn[i], b = inn[i + 1], k2 = (k + 1) % N;
    if (gableOpen(inner, i, k)) continue;
    m.quad(b[k2], b[k], a[k], a[k2]);                                  // inward: the underside of each slope, the gable's inner face
  }
  const ilo = inn[0], ihi = inn[inn.length - 1];
  for (let i = 0; i + 1 < inn.length; i++) for (const k of ends) {
    if (!gableOpen(levels, i, k)) continue;
    const a = rings[i], b = rings[i + 1], ia = inn[i], ib = inn[i + 1], k2 = (k + 1) % N;
    m.quad(a[k], b[k], ib[k], ia[k]); m.quad(b[k2], a[k2], ia[k2], ib[k2]);   // the verges of an open gable, outer to inner
  }
  for (let k = 0; k < N; k++) {
    if (ends.includes(k) && gableOpen(levels, 0, k)) continue;
    const k2 = (k + 1) % N; m.quad(ilo[k2], ilo[k], lo[k], lo[k2]);     // the eave band, outer eave to inner
  }
  fan(ihi, false);                                                      // (the roof space's top: welded away at a ridge)
  return m;
}

// A ROOF'S LEVELS OVER A CHAMFERED PLAN: the chamfer `c` (along each side, in the wall plane, level 0 of `levels0` --
// the levels before any overhang) carried up every level: a level whose sides have come in by dx and dz has its
// corner face come in as far as the slopes beside it, so its chamfer is c - dx - dz + sqrt 2 max(dx, dz) (out at the
// eave, in up the roof, gone at a ridge)
export function chamferLevels(levels, levels0, c) {
  const a = levels0[0].x1, b = levels0[0].z1;
  return levels.map((L) => { const dx = a - L.x1, dz = b - L.z1; return { ...L, c: Math.max(0, c - dx - dz + Math.SQRT2 * Math.max(dx, dz)) }; });
}

// A CHINESE ROOF: any form's levels (roofLevels, then overhang) with its slopes bent into the jujia section and its
// eave corners turned up. The stack is first cut finer -- `steps` levels over the whole height, shared out between the
// form's own levels by the height each climbs -- and every level is then raised along the concave curve: a straight
// roof's height share t becomes F(t) = (lo t + (hi - lo) t^2 / 2) / ((lo + hi) / 2), the section profiles.js `jujia`
// draws (slope lo at the eave, hi at the ridge, in proportion to the straight roof's). A vertical side stays vertical,
// so a gable, a gablet's gable (the xieshan's) and a hip bend alike. Each level's sides are cut into `perSide` pieces
// so the EAVE can rise toward its corners -- `upturn` metres at a corner, falling off as (1 - d/reach)^2 over `reach`
// metres of the side, and dying away up the roof as (1 - t)^2 -- and sweep OUT there by `flare` metres, square to each
// side (a corner, on two sides, goes out diagonally). The hips then curve up at their feet, the way a Chinese roof's
// do. Every level has the same number of points, so the stack still closes exactly; the soffit is fanned from the
// middle of the eave and a last level with an area gets a lid.
export function curvedRoof(m, levels, { lo = .35, hi = 1.2, steps = 6, upturn = 0, flare = 0, reach, perSide = 6 } = {}) {
  const y0 = levels[0].y, H = levels[levels.length - 1].y - y0;
  if (!(H > 0)) throw new Error("a curved roof needs a form that rises");
  const F = (t) => (lo * t + (hi - lo) * t * t / 2) / ((lo + hi) / 2);
  const lv = [levels[0]];
  for (let i = 0; i + 1 < levels.length; i++) {
    const A = levels[i], B = levels[i + 1], k = Math.max(1, Math.round(steps * (B.y - A.y) / H));
    for (let j = 1; j <= k; j++) {
      const f = j / k, at = (key) => A[key] + (B[key] - A[key]) * f;
      lv.push({ x0: at("x0"), x1: at("x1"), z0: at("z0"), z1: at("z1"), y: at("y") });
    }
  }
  const E = levels[0], S = Math.max(1, Math.round(perSide));
  const R = reach ?? .35 * Math.min(E.x1 - E.x0, E.z1 - E.z0);
  const outN = [[0, -1], [1, 0], [0, 1], [-1, 0]];               // each side's outward normal, in the ring's order
  const rings = lv.map((L) => {
    const t = (L.y - y0) / H, w = (1 - t) ** 2, y = y0 + H * F(t);
    const C = [[L.x0, L.z0], [L.x1, L.z0], [L.x1, L.z1], [L.x0, L.z1]];
    const pts = [];
    for (let s = 0; s < 4; s++) {
      const [ax, az] = C[s], [bx, bz] = C[(s + 1) % 4], len = Math.hypot(bx - ax, bz - az);
      for (let q = 0; q < S; q++) {
        const u = q / S, d = Math.min(u, 1 - u) * len, e = R > 0 ? Math.max(0, 1 - d / R) ** 2 : 0;
        let x = ax + (bx - ax) * u, z = az + (bz - az) * u;
        const push = flare * w * e;
        x += outN[s][0] * push; z += outN[s][1] * push;
        if (q === 0) { const p = outN[(s + 3) % 4]; x += p[0] * flare * w; z += p[1] * flare * w; }   // (a corner is on the side before, too)
        pts.push(m.vert(x, y + upturn * w * e, z));
      }
    }
    return pts;
  });
  const N = 4 * S;
  for (let i = 0; i + 1 < rings.length; i++) for (let k = 0; k < N; k++) {
    const a = rings[i], b = rings[i + 1], k2 = (k + 1) % N;
    m.quad(a[k2], a[k], b[k], b[k2]);                                  // outward, as roofMesh winds them
  }
  const lo0 = rings[0], top = rings[rings.length - 1], T = lv[lv.length - 1];
  const c0 = m.vert((E.x0 + E.x1) / 2, y0, (E.z0 + E.z1) / 2);
  for (let k = 0; k < N; k++) m.tri(c0, lo0[k], lo0[(k + 1) % N]);   // the soffit, facing down
  if ((T.x1 - T.x0) * (T.z1 - T.z0) > 1e-9) {
    const c1 = m.vert((T.x0 + T.x1) / 2, T.y, (T.z0 + T.z1) / 2);
    for (let k = 0; k < N; k++) m.tri(c1, top[(k + 1) % N], top[k]);
  }
  return m;
}

// THE FORMS, as their levels. `a`, `b` are the half-width (across the ridge, x) and half-length (along it, z);
// `pitch` the main slope in degrees. Each form reads only what it needs:
//   flat        a slab `thickness` deep
//   shed        one slope rising toward +x -- the lean-to, the mono-pitch
//   gable       two slopes to a ridge, the ends vertical
//   hip         four slopes: the ridge shortened by a hip at each end (a square plan makes it a pyramid)
//   pyramid     four slopes to one apex -- the pavilion, the tented roof
//   mansard     a steep `lowerPitch` all round to `breakH`, then a hip at `pitch` over it
//   gambrel     the same on the long sides only: a barn's roof, gabled at the ends
//   jerkinhead  a gable whose top `clip` of the height is hipped back (the clipped gable, the Krueppelwalm)
//   gablet      a hip to `hipH` of the height with a small gable over it (the Dutch gable)
//   saltbox     a gable with its ridge `ridge` of the way across: a short slope and a long one
export function roofLevels(form, { a, b, pitch = 35, thickness = .3, lowerPitch = 70, breakH, clip = .3, hipH = .6, ridge = .35 }) {
  const T = Math.tan(pitch * Math.PI / 180), R = (x0, x1, z0, z1, y) => ({ x0, x1, z0, z1, y });
  const full = R(-a, a, -b, b, 0);
  const hipTo = (L, y0) => {                            // a hip over a level: all four sides at the main pitch
    const ha = (L.x1 - L.x0) / 2, hb = (L.z1 - L.z0) / 2, mm = Math.min(ha, hb);
    const cx = (L.x0 + L.x1) / 2, cz = (L.z0 + L.z1) / 2;
    return R(cx - (ha - mm), cx + (ha - mm), cz - (hb - mm), cz + (hb - mm), y0 + mm * T);
  };
  switch (form) {
    case "flat": return [full, R(-a, a, -b, b, thickness)];
    case "shed": return [full, R(a, a, -b, b, 2 * a * T)];
    case "gable": return [full, R(0, 0, -b, b, a * T)];
    case "hip": return [full, hipTo(full, 0)];
    case "pyramid": return [full, R(0, 0, 0, 0, Math.min(a, b) * T)];
    case "saltbox": {
      const xr = -a + 2 * a * Math.max(.05, Math.min(.95, ridge));
      return [full, R(xr, xr, -b, b, (xr + a) * T)];
    }
    case "mansard": case "gambrel": {
      const L = Math.tan(lowerPitch * Math.PI / 180), h = breakH ?? a * .9, i = h / L;
      if (i >= Math.min(a, form === "mansard" ? b : a)) throw new Error(`the mansard's lower slope (${h.toFixed(2)}m at ${lowerPitch} degrees) meets itself before the break`);
      const brk = form === "mansard" ? R(-a + i, a - i, -b + i, b - i, h) : R(-a + i, a - i, -b, b, h);
      return form === "mansard" ? [full, brk, hipTo(brk, h)] : [full, brk, R(0, 0, -b, b, h + (a - i) * T)];
    }
    case "jerkinhead": {
      const H = a * T, yc = H * (1 - Math.max(.02, Math.min(.98, clip))), rest = a - yc / T;
      if (rest >= b) throw new Error("the jerkinhead's clip is longer than the roof");
      return [full, R(-rest, rest, -b, b, yc), R(0, 0, -b + rest, b - rest, H)];
    }
    case "gablet": {
      const H = a * T, y1 = H * Math.max(.02, Math.min(.98, hipH)), i = y1 / T;
      if (i >= b) throw new Error("the gablet's hip is longer than the roof");
      return [full, R(-a + i, a - i, -b + i, b - i, y1), R(0, 0, -b + i, b - i, H)];
    }
  }
  throw new Error(`roof form "${form}" is not one of flat, shed, gable, hip, pyramid, mansard, gambrel, jerkinhead, gablet, saltbox`);
}

// THE OVERHANG: the eave carried out past the wall, down its own slope. `y` 0 is where the roof meets the wall
// plane; the eave drops by as much as the MAIN slope falls over `overhang`, and every sloped side reaches out
// as far as its own slope needs to fall that much -- so a saltbox's long side and its short one end on one
// level eave. A vertical side (a gable, a shed's high wall) is carried out by `overhang` as a verge, on every
// level for as long as it stays vertical.
// `verge` false: the vertical sides stay in the wall plane (a SHELL roof's underside: the verge is the covering's alone).
export function overhang(levels, o, verge = true) {
  if (!(o > 0)) return levels;
  const out = levels.map((L) => ({ ...L }));
  const [L0, L1] = out;
  const sides = [["x0", -1], ["x1", 1], ["z0", -1], ["z1", 1]];
  const inset = (k, sgn, A, B) => (A[k] - B[k]) * sgn;        // how far a side comes in between two levels
  const slope = (k, sgn) => { const i = inset(k, sgn, L0, L1); return i > 1e-9 ? (L1.y - L0.y) / i : null; };
  const main = sides.map(([k, s]) => slope(k, s)).find((v) => v !== null);
  const drop = main ? o * main : 0;
  for (const [k, sgn] of sides) {
    const sl = slope(k, sgn);
    if (sl !== null) { out[0][k] += sgn * drop / sl; continue; }
    if (!verge) continue;
    for (let i = 0; i < out.length; i++) {                      // a verge: out, as long as the side is vertical
      if (i > 0 && Math.abs(levels[i][k] - levels[i - 1][k]) > 1e-9) break;
      out[i][k] += sgn * o;
    }
  }
  out[0].y -= drop;
  return out;
}

export const straight = (t) => (x, y, side) => [x, y, -side * t];

// ...and the same line with the face moved on its own axes first: `dx` to stand a wall on its middle rather
// than its corner (so a placement puts the wall where its CENTRE is), `dy` to lift a vault's cross-section to
// the springing line it starts from.
export const straightAt = (t, dx = 0, dy = 0) => (x, y, side) => [x + dx, y + dy, -side * t];

// A BAY OF A ROUND BUILDING. The face's x runs along the OUTER circumference, so the bay spans the angle its
// width subtends there; both faces use that same angle at their own radius, which puts the side faces exactly
// on the radial planes. Neighbouring bays therefore share those planes to the last bit -- and a ring built by
// rotating one bay by 2*pi/n has no seam at all, because the rotation is exact.
export const radial = (rOuter, rInner, w) => (x, y, side) => {
  const th = (x - w / 2) / rOuter;           // the bay is centred on its own angle
  const r = side ? rInner : rOuter;
  return [r * Math.sin(th), y, r * Math.cos(th)];
};

// ...and A BAY OF A POLYGONAL ONE (a ring's `polygon`): the face laid flat on the chord between the bay's two corners,
// at the polygon's corner radii -- an octagon's eight faces flat, as its dome's webs are, not eight arcs of a drum.
// The face is as wide as that chord (2 rOuter sin(pi / n)); the inner face spans the same corners at rInner, so
// neighbouring bays meet on the radial planes through the corners as the round ones do.
export const chordal = (rOuter, rInner, n, w) => (x, y, side) => {
  const r = side ? rInner : rOuter, h = Math.PI / n, t = x / w;
  return [r * Math.sin(h) * (2 * t - 1), y, r * Math.cos(h)];
};

// ---- steps: seating and stairs ------------------------------------------------------------------------------
// A flight of steps as a CROSS-SECTION, to be swept like a vault: an arena's seating and the stairs that climb
// through it are the same shape at different scales -- a tier of rows is a staircase with a metre-deep tread
// and a half-metre rise, a vomitorium's flight is one with a 30cm tread and an 18cm rise.
//
// It is built from its OUTLINE -- the base line and the zigzag of treads and risers -- and fanned, not filled
// as a grid of cells. Both are exact, but the grid spends a triangle on every cell under the steps (a
// thirty-three step flight costs eleven hundred of them, all masonry nobody sees) where the outline spends
// two per step.
//
// WHICH CORNER THE FAN STARTS FROM MATTERS, and only exact arithmetic reveals it. On an evenly rising flight
// every tread's inner corner lies on one straight line through the bottom-INNER corner -- they are the
// sampling of a constant slope -- so a fan from there lays each diagonal along that same line, through every
// earlier corner: a T-junction per step. From the bottom-OUTER corner no two diagonals can be parallel, and
// the fan is clean. (Rounding hid this until the rows were derived exactly; the check found it at once.)
// `landing` (rising out only) lengthens the last tread by that much: the platform a flight arrives on, as part of
// the same solid rather than a block set against its end.
// `soffit: [yIn, yOut]`: its underside a straight slope from the inner end to the outer instead of level at `base` (which
// still sets the treads' heights) -- the seating carried on a raking vault over a stair that climbs under it
// `strips`: the section cut into one strip a tread, from the base up, instead of a fan across the whole flight -- for a
// flight carried ALONG a ring (assemble.js `along`), whose sides are cylinders: a fan's triangle reaching across twenty
// treads is a chord of that curve, cutting a hand's breadth or more into the stair beside it
export function stepsFace(cols, run, rise, { base = 0, rising = "out", first = rise, landing = 0, soffit = null, strips = false } = {}) {
  const pts = [], seen = new Map(), tris = [];
  const P = (x, y) => {
    const k = `${Math.round(x * Q)},${Math.round(y * Q)}`;
    let i = seen.get(k);
    if (i === undefined) { i = pts.length; pts.push([x, y]); seen.set(k, i); }
    return i;
  };
  if (first !== rise && rising !== "out") throw new Error("a first-step height is only defined for steps rising outward");
  const top = rising === "out" ? base + first + (cols - 1) * rise : base + cols * rise;
  const [b0, b1] = soffit ?? [base, base];
  const poly = [P(0, b0)];                                    // the bottom corner, and the fan's origin
  if (rising === "out") {
    // the first tread stands one riser above the base: put it ON the base and the outline doubles back along
    // its own bottom edge, which is a sliver of zero area and a T-junction at either end of it
    // `first` is the height of the FIRST tread above the base, `rise` of every one after it. They differ when
    // the mass is not itself a flight but the ground under one: the seating carried over a vomitorium stands
    // on the tunnel's head and its first tread is already as high as the row its neighbours have reached, so
    // that the rows run across the covered bay at exactly the heights they have either side of it.
    const end = cols * run + landing;
    for (let j = 0; j < cols; j++) {                          // riser, tread, riser, tread...
      const y = base + first + j * rise;
      poly.push(P(j * run, y), P(j + 1 < cols ? (j + 1) * run : end, y));
    }
    poly.push(P(end, b1));                                     // down the outer end to close on the base
  } else {
    poly.push(P(0, top));
    for (let j = 0; j < cols; j++) {
      poly.push(P(j * run, top - j * rise), P((j + 1) * run, top - j * rise));
    }
    poly.push(P(cols * run, b1));
  }
  const endX = rising === "out" ? cols * run + landing : cols * run;
  const yb = (x) => b0 + (b1 - b0) * x / (endX || 1);
  if (strips) for (let j = cols - 1; j >= 1; j--) poly.push(P(j * run, yb(j * run)));   // (the base, back, a point under every riser)
  // tag each outline segment, so a part can ask for the treads without the underside it stands on
  const tag = new Map();
  const mark = (a, b, t) => tag.set(a < b ? `${a},${b}` : `${b},${a}`, t);
  const uniq = poly.filter((v, i) => v !== poly[(i + poly.length - 1) % poly.length]);
  for (let i = 0; i < uniq.length; i++) {
    const a = uniq[i], b = uniq[(i + 1) % uniq.length];
    const [ax, ay] = pts[a], [bx, by] = pts[b];
    const onBase = (x, y) => Math.abs(y - (b0 + (b1 - b0) * x / ((rising === "out" ? cols * run + landing : cols * run) || 1))) < 1e-9;
    mark(a, b, onBase(ax, ay) && onBase(bx, by) && Math.abs(ax - bx) > 1e-9 ? "base"
              : Math.abs(ax - bx) < 1e-9 && Math.abs(ax) < 1e-9 ? "end-in"
              : Math.abs(ax - bx) < 1e-9 && Math.abs(ax - (cols * run + (rising === "out" ? landing : 0))) < 1e-9 ? "end-out"
              : "top");
  }
  if (strips) {
    // each tread's strip: its two base corners, then up its right edge and down its left, every outline corner on them
    // (counter-clockwise); fanned from the base corner on the side with the one corner over it, so no triangle is a sliver
    for (let j = 0; j < cols; j++) {
      const xl = j * run, xr = j + 1 < cols ? (j + 1) * run : endX;
      const on = (x) => pts.map((q, i) => [q, i]).filter(([q]) => Math.abs(q[0] - x) < 1e-9 && Math.abs(q[1] - yb(x)) > 1e-9);
      const right = on(xr).sort((a, b) => a[0][1] - b[0][1]).map(([, i]) => i);
      const left = on(xl).sort((a, b) => b[0][1] - a[0][1]).map(([, i]) => i);
      // (only what bounds this strip: the left edge up to this tread, the right up to it -- a taller corner over the
      //  edge is the next tread's, rising in, or the last one's, rising out)
      const yT = rising === "out" ? base + first + j * rise : top - j * rise;
      const R = right.filter((i) => pts[i][1] <= yT + 1e-9), L = left.filter((i) => pts[i][1] <= yT + 1e-9);
      const ring = [P(xl, yb(xl)), P(xr, yb(xr)), ...R, ...L];
      const f = rising === "out" ? 1 : 0;                        // (out: from the bottom right; in: the bottom left)
      for (let k = 1; k + 1 < ring.length; k++) {
        const a = ring[f], b = ring[(f + k) % ring.length], c = ring[(f + k + 1) % ring.length];
        tris.push([a, b, c]);
      }
    }
    return { ...closeFace(pts, tris), tag, cols, run, rise, top };
  }
  const o = uniq.indexOf(rising === "out" ? P(cols * run + landing, b1) : P(0, b0));   // the far bottom corner
  // (counter-clockwise, as every other face is: the outline runs clockwise, so the fan is turned round --
  //  it used to be drawn as it came, and every flight and tier of seating was wound inside out)
  let s2 = 0;
  for (let i = 0; i < uniq.length; i++) { const [x0, y0] = pts[uniq[i]], [x1, y1] = pts[uniq[(i + 1) % uniq.length]]; s2 += x0 * y1 - x1 * y0; }
  for (let k = 1; k + 1 < uniq.length; k++) {
    const a = uniq[o], b = uniq[(o + k) % uniq.length], c = uniq[(o + k + 1) % uniq.length];
    tris.push(s2 < 0 ? [a, c, b] : [a, b, c]);
  }
  return { ...closeFace(pts, tris), tag, cols, run, rise, top };
}

// A TUNNEL'S LONG SECTION. A passage under a building is the void between a floor line and a ceiling line, and a
// stair's tunnel has both on the slope: the ceiling is NOT stepped, it runs straight at the flight's own angle a
// head's height above it (and flat over a landing, where the floor is flat). The face is that quadrilateral --
// x along the passage, y up -- so extruding it across the passage's width gives the ceiling ("top"), the floor
// ("base", rarely wanted: the stair is its own part), the two side walls ("sides": exactly the wall between floor
// line and ceiling line, no masonry drawn above or below what can be seen) and the two open ends.
export function tunnelFace(length, floorIn, floorOut, ceilIn, ceilOut) {
  const pts = [[0, floorIn], [length, floorOut], [length, ceilOut], [0, ceilIn]], tag = new Map();
  tag.set("0,1", "base"); tag.set("1,2", "end-out"); tag.set("2,3", "top"); tag.set("0,3", "end-in");
  return { ...closeFace(pts, [[0, 1, 2], [0, 2, 3]]), tag };
}

