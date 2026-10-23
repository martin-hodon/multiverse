// THE ITEMS (2026-09-28; docs/items.md): what a hand holds and what a room is furnished with -- a sword, a shield, a
// scythe, a lute, a chair, a four-poster -- as DEFINITIONS (assets/items/**.json), built into triangles by this one
// module wherever they are drawn: the asset viewer, the tools in people's hands (tools.js), the furniture in a
// building (architecture.js). Nothing here touches three: out come plain arrays, one set per MATERIAL, and the
// materials are named (oak, walnut, iron, leather, rush...) and textured from the pattern library.
//
// A definition stands on others (`use`, defs.js) and is made of PARTS -- primitives (a rod, a lathe-turned profile, a
// box, a sweep along a curve, a blade, a plate, a shield) and COMPONENTS (another item asked for by path, with its own
// params: a turned leg, a pommel, a crossguard, an axe head). A HOLD says where a hand closes on it.
import { evalValue } from "./expr.js";
import { flatten, isPlain } from "./defs.js";
import { earClip } from "./arch/build.js";
import { faceGeometry } from "./face.js";
import { hairGeometry } from "./hair.js";
import { feathersGeometry } from "./feathers.js";
import { petalsGeometry } from "./petals.js";
import { strandGeometry, collarGeometry, bandGeometry, onFrames } from "./jewelry.js";   // what is worn on the body, on guides from it   // a whorl of petals (a flower, its sepals, a leaf pair)

const DEG = Math.PI / 180;
function rng(seed) {
  let a = (seed >>> 0) || 1;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

// ---- PARAMS ---------------------------------------------------------------------------------------------------------
// A param is a number, an expression over the params before it, a word ("cross", "oak"), a RANGE [lo, hi] -- a
// value in it, drawn by the item's seed, so every sword of a kind is a little its own -- or { "pick": [...] }, one of
// a list (numbers, words, anything), also by the seed.
// a value: an expression -- or the NAME of a param holding a word ("guardStyle" -> "cross"): the parser reads words as
// numbers or gives them back as written, and a word param named by another definition must arrive as its word
// (or a param holding an OBJECT -- a fit to lie on, a hairstyle's cap: jewelry.js -- handed on by its name as it is)
const val = (v, P) => typeof v === "boolean" || v === null ? v
  : typeof v === "string" && Object.prototype.hasOwnProperty.call(P, v) && (typeof P[v] === "string" || (P[v] !== null && typeof P[v] === "object")) ? P[v] : evalValue(v, P);
const isRange = (v) => Array.isArray(v) && v.length === 2 && v.every((x) => typeof x === "number");
function drawValue(v, P, r) {
  if (isRange(v)) return v[0] + (v[1] - v[0]) * r();
  if (isPlain(v) && Array.isArray(v.pick)) return drawValue(v.pick[Math.floor(r() * v.pick.length) % v.pick.length], P, r);
  return typeof v === "string" || typeof v === "number" ? val(v, P) : v;
}
function paramsOf(def, over, r) {
  const P = {};
  const all = { ...(def.params ?? {}), ...over };
  for (const [k, v] of Object.entries(all)) P[k] = drawValue(v, P, r);
  return P;
}
// `when`: a part a variant has not got. A name (the param is true), a list (all are), or { "guard": "cross" } /
// { "guard": ["cross", "knuckle"] } (the param IS that word, or one of those)
function passes(when, P) {
  if (when === undefined) return true;
  if (isPlain(when)) return Object.entries(when).every(([k, v]) => (Array.isArray(v) ? v : [v]).includes(P[k]));
  return (Array.isArray(when) ? when : [when]).every((n) => !!P[n]);
}
// a part's numbers resolved (its words -- type, material, use, shape, charge -- kept as they are)
const WORDS = new Set(["id", "type", "material", "rimMaterial", "backMaterial", "materials", "use", "shape", "charge", "_about", "role", "when", "name", "params", "mirror", "tips", "throatMaterial", "fit", "bead", "kind", "ground"]);
function resolvePart(p, P) {
  const out = {};
  for (const [k, v] of Object.entries(p)) {
    if (WORDS.has(k)) {   // (a word may name a word param: "shape": "shape" is the shield's own shape, "material": "legWood")
      out[k] = (k === "shape" || k.endsWith("aterial") || k === "charge" || k === "use") && typeof v === "string" && typeof P[v] === "string" ? P[v] : v;
      continue;
    }
    out[k] = deep(v, P);
  }
  return out;
}
const deep = (v, P) => Array.isArray(v) ? v.map((x) => deep(x, P)) : isPlain(v) ? Object.fromEntries(Object.entries(v).map(([k, x]) => [k, WORDS.has(k) ? x : deep(x, P)])) : val(v, P);

// ---- PLACEMENTS: 3x4 affine matrices [r00 r01 r02 tx, r10 r11 r12 ty, r20 r21 r22 tz] --------------------------------
const I3 = () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0];
function mul(A, B) {   // A * B
  const o = new Array(12);
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) o[r * 4 + c] = A[r * 4] * B[c] + A[r * 4 + 1] * B[4 + c] + A[r * 4 + 2] * B[8 + c];
    o[r * 4 + 3] = A[r * 4] * B[3] + A[r * 4 + 1] * B[7] + A[r * 4 + 2] * B[11] + A[r * 4 + 3];
  }
  return o;
}
// [x, y, z, yaw, pitch, roll] (degrees; yaw about y, then pitch about x, then roll about z) and a uniform scale
function placeM(at = [0, 0, 0], s = 1) {
  const [x = 0, y = 0, z = 0, yaw = 0, pitch = 0, roll = 0] = at;
  const cy = Math.cos(yaw * DEG), sy = Math.sin(yaw * DEG), cp = Math.cos(pitch * DEG), sp = Math.sin(pitch * DEG), cr = Math.cos(roll * DEG), sr = Math.sin(roll * DEG);
  const Ry = [cy, 0, sy, 0, 0, 1, 0, 0, -sy, 0, cy, 0], Rx = [1, 0, 0, 0, 0, cp, -sp, 0, 0, sp, cp, 0], Rz = [cr, -sr, 0, 0, sr, cr, 0, 0, 0, 0, 1, 0];
  const M = mul(Ry, mul(Rx, Rz));
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) M[r * 4 + c] *= s;
  M[3] = x; M[7] = y; M[11] = z;
  return M;
}
const MIRROR_X = [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0], MIRROR_Z = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0];
// a part's placements: `at` (one or a list), `along` { n, from, to } (n copies evenly from..to, their own yaw etc. from
// `at`'s), `around` { n, r, plane: "xz" (a ring on the floor: legs, spokes, flanges -- each turned to face out) or "xy"
// (a ring upright: studs round a shield, numerals round a dial), start, span } , `mirror` "x" (each also reflected
// across x = 0) or "z" (across z = 0: a ship's two sides) -- each composed onto the parent's
function placementsOf(p, parent, P = {}) {
  const ats = p.at === undefined ? [[0, 0, 0]] : Array.isArray(p.at[0]) ? p.at : [p.at];
  let list = ats;
  if (p.along) {
    const { n, from, to } = p.along, k = Math.max(1, Math.round(n));
    list = [];
    for (const a of ats) for (let i = 0; i < k; i++) {
      const t = k === 1 ? .5 : i / (k - 1);
      list.push([from[0] + (to[0] - from[0]) * t + (a[0] ?? 0), from[1] + (to[1] - from[1]) * t + (a[1] ?? 0), from[2] + (to[2] - from[2]) * t + (a[2] ?? 0), a[3] ?? 0, a[4] ?? 0, a[5] ?? 0]);
    }
  }
  if (p.around) {
    const { n, r = 0, plane = "xz", start = 0, span = 360 } = p.around, k = Math.max(1, Math.round(n)), full = Math.abs(span) >= 359.9;
    list = [];
    for (const a of ats) for (let i = 0; i < k; i++) {
      const deg = start + span * (full ? i / k : k === 1 ? 0 : i / (k - 1)), t = deg * DEG;
      if (plane === "xy") list.push([(a[0] ?? 0) + r * Math.cos(t), (a[1] ?? 0) + r * Math.sin(t), a[2] ?? 0, a[3] ?? 0, a[4] ?? 0, (a[5] ?? 0) + deg - 90]);
      else list.push([(a[0] ?? 0) + r * Math.cos(t), a[1] ?? 0, (a[2] ?? 0) - r * Math.sin(t), (a[3] ?? 0) + deg, a[4] ?? 0, a[5] ?? 0]);
    }
  }
  // (`stretch` [sx, sy, sz]: the part drawn out along the PARENT's axes, about its own place, after it is turned -- a
  //  lute's pear flattened front to back, a square turned 45 degrees and then drawn out into an oblong)
  const st = p.stretch ? [p.stretch[0], 0, 0, 0, 0, p.stretch[1], 0, 0, 0, 0, p.stretch[2], 0] : null;
  const local = list.map((a) => {
    if (!st) return placeM(a, p.scale ?? 1);
    const R = placeM([0, 0, 0, a[3] ?? 0, a[4] ?? 0, a[5] ?? 0], p.scale ?? 1), SR = mul(st, R);
    SR[3] = a[0] ?? 0; SR[7] = a[1] ?? 0; SR[11] = a[2] ?? 0;
    return SR;
  });
  // (the mirror is in the part's OWN frame -- the frame its `at` is written in -- so a yard's two arms stay a yard
  //  when the sail is turned across the ship)
  const mirrored = p.mirror === "x" ? local.map((M) => mul(MIRROR_X, M)) : p.mirror === "z" ? local.map((M) => mul(MIRROR_Z, M)) : [];
  // `on`: set on a FIT's surface (jewelry.js: a pendant on the chest, a wreath's leaves round the head, an earring at
  // the lobe) -- each frame there, its x round the body, y up the surface, z out of it; `at` is then in that frame
  if (p.on) return onFrames(p.on, P).flatMap((F) => [...local, ...mirrored].map((M) => mul(parent, mul(F, M))));
  return [...local, ...mirrored].map((M) => mul(parent, M));
}

// ---- THE SINK: one material's triangles, placed as they are emitted -------------------------------------------------
// Every primitive emits in its own frame: vert(position, normal, uv) and tri(a, b, c). A triangle is turned to face
// the way its vertices' normals say (compared after placing: a mirrored copy comes out wound right by itself).
function emitter(sink, M) {
  // the normal matrix: the inverse transpose (the cofactors over the determinant -- a mirror or a stretch turn normals
  // as they must)
  const [a, b, c, , d, e0, f, , g, h, i] = M, det = a * (e0 * i - f * h) - b * (d * i - f * g) + c * (d * h - e0 * g) || 1;
  const Nm = [(e0 * i - f * h) / det, (f * g - d * i) / det, (d * h - e0 * g) / det,
              (c * h - b * i) / det, (a * i - c * g) / det, (b * g - a * h) / det,
              (b * f - c * e0) / det, (c * d - a * f) / det, (a * e0 - b * d) / det];
  const e = {
    vert(p, n, uv) {
      const x = M[0] * p[0] + M[1] * p[1] + M[2] * p[2] + M[3], y = M[4] * p[0] + M[5] * p[1] + M[6] * p[2] + M[7], z = M[8] * p[0] + M[9] * p[1] + M[10] * p[2] + M[11];
      const nx = Nm[0] * n[0] + Nm[1] * n[1] + Nm[2] * n[2], ny = Nm[3] * n[0] + Nm[4] * n[1] + Nm[5] * n[2], nz = Nm[6] * n[0] + Nm[7] * n[1] + Nm[8] * n[2];
      const l = Math.hypot(nx, ny, nz) || 1;
      sink.pos.push(x, y, z); sink.nor.push(nx / l, ny / l, nz / l); sink.uv.push(uv[0], uv[1]);
      return sink.pos.length / 3 - 1;
    },
    tri(a, b, c) {
      if (a === b || b === c || a === c) return;
      const P = sink.pos, N = sink.nor;
      const ux = P[b * 3] - P[a * 3], uy = P[b * 3 + 1] - P[a * 3 + 1], uz = P[b * 3 + 2] - P[a * 3 + 2];
      const vx = P[c * 3] - P[a * 3], vy = P[c * 3 + 1] - P[a * 3 + 1], vz = P[c * 3 + 2] - P[a * 3 + 2];
      const fx = uy * vz - uz * vy, fy = uz * vx - ux * vz, fz = ux * vy - uy * vx;
      const nx = N[a * 3] + N[b * 3] + N[c * 3], ny = N[a * 3 + 1] + N[b * 3 + 1] + N[c * 3 + 1], nz = N[a * 3 + 2] + N[b * 3 + 2] + N[c * 3 + 2];
      if (fx * nx + fy * ny + fz * nz < 0) sink.idx.push(a, c, b); else sink.idx.push(a, b, c);
    },
    quad(a, b, c, d) { e.tri(a, b, c); e.tri(a, c, d); },
  };
  return e;
}

// ---- PRIMITIVES (each in its own frame, metres) ---------------------------------------------------------------------
// how many sides a round thing gets when its definition doesn't say: 8 up to a 5 cm radius (an oar's loom, a leg, a
// cup -- more is not noticed; 6 under a centimetre: a wire, a hoop, a bail), then growing with the radius (a wheel, a column, a table top) to `max`
const sidesFor = (r, P, min = 5, max = 32) => Math.max(min, Math.min(max, Math.round((r < .01 ? 6 : 8 + 90 * Math.max(0, r - .05)) * (P.detail ?? 1))));

// LATHE: a profile [[r, y], ...] turned about the y axis. Each profile segment is a band of its own (its normal from
// its own slope: turned work has its edges -- a bead, a fillet, a cup -- where the profile turns). Caps where the
// profile starts or ends off the axis. uv: along the profile (the grain runs along a turned leg), round the ring.
function lathe(e, profile, sides, { capLo = true, capHi = true, faceted = false } = {}) {
  let along = 0;
  for (let k = 0; k + 1 < profile.length; k++) {
    const [r0, y0] = profile[k], [r1, y1] = profile[k + 1];
    const dr = r1 - r0, dy = y1 - y0, len = Math.hypot(dr, dy);
    if (len < 1e-9 || (r0 < 1e-9 && r1 < 1e-9)) continue;
    const nr = dy / len, ny = -dr / len, rm = Math.max((r0 + r1) / 2, 1e-4);
    if (faceted) {   // (flat faces round: a square leg, an octagonal post -- each face its own normal, not smoothed round)
      for (let i = 0; i < sides; i++) {
        const a0 = i / sides * Math.PI * 2, a1 = (i + 1) / sides * Math.PI * 2, am = (a0 + a1) / 2, n = [nr * Math.cos(am) / Math.cos(Math.PI / sides), ny, nr * Math.sin(am) / Math.cos(Math.PI / sides)];
        const q = [[r0, y0, a0, along], [r0, y0, a1, along], [r1, y1, a1, along + len], [r1, y1, a0, along + len]].map(([r, y, a, u]) => e.vert([r * Math.cos(a), y, r * Math.sin(a)], n, [u, a * rm]));
        e.quad(q[0], q[1], q[2], q[3]);
      }
      along += len; continue;
    }
    const ring0 = [], ring1 = [];
    for (let i = 0; i <= sides; i++) {
      const a = i / sides * Math.PI * 2, c = Math.cos(a), s = Math.sin(a), n = [nr * c, ny, nr * s];
      ring0.push(e.vert([r0 * c, y0, r0 * s], n, [along, a * rm]));
      ring1.push(e.vert([r1 * c, y1, r1 * s], n, [along + len, a * rm]));
    }
    for (let i = 0; i < sides; i++) e.quad(ring0[i], ring0[i + 1], ring1[i + 1], ring1[i]);
    along += len;
  }
  const cap = (r, y, up) => {
    if (r < 1e-9) return;
    const n = [0, up ? 1 : -1, 0], c0 = e.vert([0, y, 0], n, [0, 0]), ring = [];
    for (let i = 0; i <= sides; i++) { const a = i / sides * Math.PI * 2; ring.push(e.vert([r * Math.cos(a), y, r * Math.sin(a)], n, [r * Math.cos(a), r * Math.sin(a)])); }
    for (let i = 0; i < sides; i++) e.tri(c0, ring[i], ring[i + 1]);
  };
  if (capLo) cap(profile[0][0], profile[0][1], false);
  if (capHi) cap(profile[profile.length - 1][0], profile[profile.length - 1][1], true);
}
// the frame that turns +y onto a direction (for a rod, a lathe laid along any axis)
function alongM(from, dir) {
  const L = Math.hypot(...dir) || 1, y = dir.map((v) => v / L);
  const ref = Math.abs(y[1]) < .9 ? [0, 1, 0] : [1, 0, 0];
  let x = [ref[1] * y[2] - ref[2] * y[1], ref[2] * y[0] - ref[0] * y[2], ref[0] * y[1] - ref[1] * y[0]];
  const lx = Math.hypot(...x); x = x.map((v) => v / lx);
  const z = [x[1] * y[2] - x[2] * y[1], x[2] * y[0] - x[0] * y[2], x[0] * y[1] - x[1] * y[0]];
  return [x[0], y[0], z[0], from[0], x[1], y[1], z[1], from[1], x[2], y[2], z[2], from[2]];
}

// BOX: `size` [w, h, d] centred on its origin; `round` rounds its edges and corners (a cushion, a mattress -- only
// soft things: a part in a fabric takes it, wood is six faces whatever it says). uv: on each face, the grain along
// the face's longer side.
function box(e, [w, h, d], round = 0, P = {}) {
  const hs = [w / 2, h / 2, d / 2], R = Math.min(round, ...hs.map((v) => v * .98));
  const m = R > 1e-6 ? Math.max(2, Math.round(2 * (P.detail ?? 1))) : 0;
  // along each axis: the corner arc's samples at both ends, flat between (just the two ends when square)
  const axisPts = (hv) => {
    if (!m) return [-hv, hv];
    const pts = [];
    for (let i = 0; i <= m; i++) pts.push(-hv + R * (1 - Math.sin(i / m * Math.PI / 2)));
    for (let i = m; i >= 0; i--) pts.push(hv - R * (1 - Math.sin(i / m * Math.PI / 2)));
    return pts;
  };
  const inner = hs.map((v) => v - R);
  const faces = [[0, 1], [0, -1], [1, 1], [1, -1], [2, 1], [2, -1]];   // [axis, sign]
  for (const [ax, sg] of faces) {
    const u = (ax + 1) % 3, v = (ax + 2) % 3;
    const us = axisPts(hs[u]), vs = axisPts(hs[v]);
    const grainU = hs[u] >= hs[v];
    const ids = [];
    for (let j = 0; j < vs.length; j++) for (let i = 0; i < us.length; i++) {
      const p0 = [0, 0, 0]; p0[ax] = sg * hs[ax]; p0[u] = us[i]; p0[v] = vs[j];
      let p = p0, n = [0, 0, 0]; n[ax] = sg;
      if (R > 1e-6) {
        const c = p0.map((x, k) => Math.max(-inner[k], Math.min(inner[k], x)));
        const dv = p0.map((x, k) => x - c[k]), l = Math.hypot(...dv);
        if (l > 1e-9) { n = dv.map((x) => x / l); p = c.map((x, k) => x + n[k] * R); }
      }
      ids.push(e.vert(p, n, grainU ? [p[u], p[v]] : [p[v], p[u]]));
    }
    const nu = us.length;
    for (let j = 0; j + 1 < vs.length; j++) for (let i = 0; i + 1 < nu; i++) e.quad(ids[j * nu + i], ids[j * nu + i + 1], ids[(j + 1) * nu + i + 1], ids[(j + 1) * nu + i]);
  }
}

// a Catmull-Rom curve through points, `seg` pieces a span (closed: round to the first again)
function curveThrough(pts, seg, closed) {
  if (pts.length < 2) return pts.slice();
  const n = pts.length, at = (i) => closed ? pts[(i + n) % n] : pts[Math.max(0, Math.min(n - 1, i))];
  const out = [], spans = closed ? n : n - 1;
  for (let s = 0; s < spans; s++) for (let k = 0; k < seg; k++) {
    const t = k / seg, a = at(s - 1), b = at(s), c = at(s + 1), d = at(s + 2);
    out.push([0, 1, 2].map((i) => b[i] + .5 * t * (c[i] - a[i] + t * (2 * a[i] - 5 * b[i] + 4 * c[i] - d[i] + t * (3 * (b[i] - c[i]) + d[i] - a[i])))));
  }
  if (!closed) out.push(pts[n - 1].slice());
  return out;
}
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(...a) || 1; return a.map((v) => v / l); };

// SWEEP: a section carried along a curve through `path` -- round (`r`, or `radii` one a point: a tapering bow limb, a
// horn), or a rectangle (`section` [w, h]: a strap, a chair's bent back rail, a bow's flat limb; `up` says which way
// its h faces). `closed`: a ring. uv: along the curve, round the section.
function sweep(e, p, P) {
  const closed = !!p.closed, seg = Math.max(2, Math.round((p.seg ?? 6) * (P.detail ?? 1)));
  const C = curveThrough(p.path, seg, closed), n = C.length;
  const rAt = (i) => {
    if (!p.radii) return p.r ?? .01;
    const f = i / Math.max(1, n - (closed ? 0 : 1)) * (p.radii.length - 1), k = Math.min(p.radii.length - 2, Math.floor(f));
    return p.radii.length === 1 ? p.radii[0] : p.radii[k] + (p.radii[k + 1] - p.radii[k]) * (f - k);
  };
  // frames by parallel transport from the first normal (or `up`)
  const T = C.map((_, i) => norm(sub(C[closed ? (i + 1) % n : Math.min(n - 1, i + 1)], C[closed ? (i - 1 + n) % n : Math.max(0, i - 1)])));
  let N0 = p.up ? p.up.slice() : Math.abs(T[0][1]) < .9 ? [0, 1, 0] : [1, 0, 0];
  N0 = norm(sub(N0, T[0].map((v) => v * dot(N0, T[0]))));
  const Ns = [N0];
  for (let i = 1; i < n; i++) {
    const prev = Ns[i - 1], t = T[i];
    Ns.push(norm(sub(prev, t.map((v) => v * dot(prev, t)))));
  }
  const Bs = T.map((t, i) => cross(t, Ns[i]));
  let along = [0];
  for (let i = 1; i < n; i++) along.push(along[i - 1] + Math.hypot(...sub(C[i], C[i - 1])));
  const rect = p.section;
  // (one count of sides for every ring: a tapering sweep's rings must match vertex for vertex, or the quads between
  //  them stitch the wrong ones -- long thin triangles between a table's legs)
  const S = p.sides ?? sidesFor(p.radii ? Math.max(...p.radii) : (p.r ?? .01), P, 5, 16);
  const ringOf = (i) => {
    const c = C[i], N = Ns[i], B = Bs[i];
    if (rect) {   // four sides, each flat: its own two vertices a corner
      const hw = rect[0] / 2 * (p.radii ? rAt(i) / (p.radii[0] || 1) : 1), hh = rect[1] / 2;
      const corners = [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]], normals = [[0, -1], [1, 0], [0, 1], [-1, 0]];
      const out = [];
      for (let k = 0; k < 4; k++) {
        const [a0, b0] = corners[k], [a1, b1] = corners[(k + 1) % 4], [na, nb] = normals[k];
        const nn = [0, 1, 2].map((q) => B[q] * na + N[q] * nb);
        out.push([e.vert([0, 1, 2].map((q) => c[q] + B[q] * a0 + N[q] * b0), nn, [along[i], k]), e.vert([0, 1, 2].map((q) => c[q] + B[q] * a1 + N[q] * b1), nn, [along[i], k + 1])]);
      }
      return out;
    }
    const r = rAt(i), s = S, out = [];
    for (let k = 0; k <= s; k++) {
      const a = k / s * Math.PI * 2, nn = [0, 1, 2].map((q) => N[q] * Math.cos(a) + B[q] * Math.sin(a));
      out.push(e.vert([0, 1, 2].map((q) => c[q] + nn[q] * r), nn, [along[i], a * r]));
    }
    return out;
  };
  const rings = C.map((_, i) => ringOf(i));
  const spans = closed ? n : n - 1;
  for (let i = 0; i < spans; i++) {
    const A = rings[i], B = rings[(i + 1) % n];
    if (rect) for (let k = 0; k < 4; k++) e.quad(A[k][0], A[k][1], B[k][1], B[k][0]);
    else for (let k = 0; k + 1 < A.length; k++) e.quad(A[k], A[k + 1], B[k + 1], B[k]);
  }
  if (!closed) for (const [i, sgn] of [[0, -1], [n - 1, 1]]) {   // the ends, capped
    const t = T[i].map((v) => v * sgn), c = e.vert(C[i], t, [0, 0]);
    const ring = rect ? [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([a, b]) => { const hw = rect[0] / 2 * (p.radii ? rAt(i) / (p.radii[0] || 1) : 1), hh = rect[1] / 2;
      return e.vert([0, 1, 2].map((q) => C[i][q] + Bs[i][q] * a * hw + Ns[i][q] * b * hh), t, [a * hw, b * hh]); })
      : (() => { const s = S, r = rAt(i);
          return Array.from({ length: s }, (_, k) => { const a = k / s * Math.PI * 2;
            return e.vert([0, 1, 2].map((q) => C[i][q] + (Ns[i][q] * Math.cos(a) + Bs[i][q] * Math.sin(a)) * r), t, [Math.cos(a) * r, Math.sin(a) * r]); }); })();
    for (let k = 0; k < ring.length; k++) e.tri(c, ring[k], ring[(k + 1) % ring.length]);
  }
}

// BLADE: along +y from its base (0) to its point (`length`), `width` [[t, half width], ...] (t 0..1 along), `thick`
// [at the base, at the point], `edges` 2 (a double-edged blade: a lens or, with `flat` > 0, a flattened diamond) or 1
// (an edge on +x, a spine on -x: a falchion, a sabre, a knife), `curve` how far the point swings back toward the spine
// (a sabre's, a scimitar's, a katana's), `fuller` (a groove down the middle, as a fraction of the width -- a darker
// flat). Flat facets, crisp edges. uv: along the blade, across it.
function blade(e, p) {
  const L = p.length, W = p.width ?? [[0, .025], [.85, .02], [1, 0]], th = p.thick ?? [.006, .002], edges = p.edges ?? 2;
  const flat = p.flat ?? .35, curve = p.curve ?? 0, stations = Math.max(6, Math.round(p.seg ?? 16));
  const hwAt = (t) => { for (let k = 1; k < W.length; k++) if (t <= W[k][0] + 1e-9) { const f = (t - W[k - 1][0]) / Math.max(1e-9, W[k][0] - W[k - 1][0]); return W[k - 1][1] + (W[k][1] - W[k - 1][1]) * f; } return W[W.length - 1][1]; };
  const section = (t) => {
    const hw = hwAt(t), h = (th[0] + (th[1] - th[0]) * t) / 2, cx = -curve * t * t, y = t * L;
    // the centre line swings back; the section stays square to the length (a curved blade's facets follow it)
    const pts = edges === 1
      ? [[-hw, h], [hw * (1 - 2 * flat), h], [hw, 0], [hw * (1 - 2 * flat), -h], [-hw, -h]]
      : [[-hw, 0], [-hw * flat, h], [hw * flat, h], [hw, 0], [hw * flat, -h], [-hw * flat, -h]];
    return pts.map(([x, z]) => [cx + x, y, z]);
  };
  const S = Array.from({ length: stations + 1 }, (_, i) => section(i / stations));
  const m = S[0].length;
  for (let i = 0; i < stations; i++) for (let k = 0; k < m; k++) {
    const a0 = S[i][k], a1 = S[i][(k + 1) % m], b0 = S[i + 1][k], b1 = S[i + 1][(k + 1) % m];
    const n = norm(cross(sub(a1, a0), sub(b0, a0)));
    const out = norm([(a0[0] + a1[0]) / 2 - (-curve * (i / stations) ** 2), 0, (a0[2] + a1[2]) / 2]);
    const nn = dot(n, out) < 0 ? n.map((v) => -v) : n;
    const ids = [a0, a1, b1, b0].map((q) => e.vert(q, nn, [q[1], q[0]]));
    e.quad(ids[0], ids[1], ids[2], ids[3]);
  }
  // the base, closed (the guard or the ferrule sits on it)
  const c = e.vert([S[0].reduce((s, q) => s + q[0], 0) / m, 0, 0], [0, -1, 0], [0, 0]), ring = S[0].map((q) => e.vert(q, [0, -1, 0], [q[0], q[2]]));
  for (let k = 0; k < m; k++) e.tri(c, ring[k], ring[(k + 1) % m]);
}

// PLATE: an outline [[x, y], ...] in the x-y plane, `thick` through z -- or `taper` [thickness at its smallest x, at its
// largest]: an axe head thick at the eye and fine at the edge. uv: the plane itself (metres).
function plate(e, p) {
  const O = p.outline, xs = O.map((q) => q[0]), x0 = Math.min(...xs), x1 = Math.max(...xs);
  const tAt = (x) => p.taper ? p.taper[0] + (p.taper[1] - p.taper[0]) * (x - x0) / Math.max(1e-9, x1 - x0) : (p.thick ?? .01);
  const tris = earClip(O, O.map((_, i) => i));
  let area = 0; for (let i = 0; i < O.length; i++) { const [ax, ay] = O[i], [bx, by] = O[(i + 1) % O.length]; area += ax * by - bx * ay; }
  const out = area >= 0 ? 1 : -1;   // (a side's normal points out of the outline whichever way round it was written)
  for (const sgn of [1, -1]) {
    const ids = O.map(([x, y]) => e.vert([x, y, sgn * tAt(x) / 2], [0, 0, sgn], [x, y]));
    for (const [a, b, c] of tris) e.tri(ids[a], ids[b], ids[c]);
  }
  for (let i = 0; i < O.length; i++) {
    const [ax, ay] = O[i], [bx, by] = O[(i + 1) % O.length];
    const n = norm([(by - ay) * out, -(bx - ax) * out, 0]), ta = tAt(ax) / 2, tb = tAt(bx) / 2, L = Math.hypot(bx - ax, by - ay);
    const q = [[ax, ay, ta], [bx, by, tb], [bx, by, -tb], [ax, ay, -ta]].map((v, k) => e.vert(v, n, [k === 1 || k === 2 ? L : 0, v[2]]));
    e.quad(q[0], q[1], q[2], q[3]);
  }
}

// ---- SHIELDS: an outline, curved across (`bend`, the radius of the curve; 0 flat) and domed (`dish`), `thick` planks;
// a RIM (`rim` wide round the face, its own material), a BOSS (`boss` [radius, height]) and the FACE painted as a
// panel fitted to the shield (the face material's pattern gets W and H) -- the heraldry, the Viking's gyronny, the
// Roman's wings, whatever the material names
export function shieldOutline(shape, w, h, n = 48) {
  const out = [], hw = w / 2, hh = h / 2;
  const arc = (cx, cy, r, a0, a1, k) => { for (let i = 0; i < k; i++) { const a = a0 + (a1 - a0) * i / k; out.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } };
  if (shape === "round" || shape === "oval") { for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; out.push([hw * Math.cos(a), hh * Math.sin(a)]); } }
  else if (shape === "kite") {         // a round top, the sides drawn in to a point (the Normans')
    const cy = hh - hw; arc(0, cy, hw, 0, Math.PI, n / 2);
    for (let i = 0; i < n / 2; i++) { const t = i / (n / 2), y = cy - (cy + hh) * t, x = -hw * (1 - t) * (1 + .35 * t); out.push([x, y]); }
    for (let i = 0; i < n / 2; i++) { const t = 1 - i / (n / 2), y = cy - (cy + hh) * t, x = hw * (1 - t) * (1 + .35 * t); out.push([x, y]); }
  } else if (shape === "heater") {     // a flat top, straight sides a third of the way, then arcs to the point
    out.push([hw, hh], [-hw, hh]);
    const y1 = hh - h * .3, R = (hw * hw + (y1 + hh) ** 2) / (2 * hw);
    for (let i = 0; i <= n / 2; i++) { const t = i / (n / 2), y = y1 - (y1 + hh) * t, cxL = -hw + R; out.push([cxL - Math.sqrt(Math.max(0, R * R - (y - y1) ** 2)), y]); }
    for (let i = n / 2 - 1; i >= 0; i--) { const t = i / (n / 2), y = y1 - (y1 + hh) * t, cxR = hw - R; out.push([cxR + Math.sqrt(Math.max(0, R * R - (y - y1) ** 2)), y]); }
  } else {                             // "rect": a scutum, a pavise -- corners rounded
    const r = Math.min(hw, hh) * .18, k = Math.max(2, n / 8);
    arc(hw - r, hh - r, r, 0, Math.PI / 2, k); arc(-hw + r, hh - r, r, Math.PI / 2, Math.PI, k);
    arc(-hw + r, -hh + r, r, Math.PI, 1.5 * Math.PI, k); arc(hw - r, -hh + r, r, 1.5 * Math.PI, 2 * Math.PI, k);
  }
  return out;
}
function shield(sinkOf, M, p, P) {
  const w = p.w, h = p.h ?? p.w, O = shieldOutline(p.shape ?? "round", w, h, Math.round(48 * (P.detail ?? 1)));
  const bend = p.bend ?? 0, dish = p.dish ?? 0, T = p.thick ?? .02, rimW = p.rim ?? 0;
  const zOf = (x, y) => (bend > 0 ? Math.sqrt(Math.max(0, bend * bend - x * x)) - bend : 0) + dish * Math.max(0, 1 - (x / (w / 2)) ** 2 - (y / (h / 2)) ** 2);
  const nOf = (x, y) => { const e = 1e-3; return norm([zOf(x - e, y) - zOf(x + e, y), zOf(x, y - e) - zOf(x, y + e), 2 * e]); };
  // rings from the outline in to the middle: the first band as wide as the rim (the rim's own material)
  const K = Math.max(4, Math.round(8 * (P.detail ?? 1))), size = Math.min(w, h) / 2, sRim = rimW > 0 ? 1 - rimW / size : 1;
  const scales = rimW > 0 ? [1, sRim, ...Array.from({ length: K }, (_, k) => sRim * (1 - (k + 1) / K))] : Array.from({ length: K + 1 }, (_, k) => 1 - k / K);
  const face = emitter(sinkOf(p.material ?? "face", { W: w, H: h }), M), rim = rimW > 0 ? emitter(sinkOf(p.rimMaterial ?? "rim"), M) : face;
  const back = emitter(sinkOf(p.backMaterial ?? "back"), M);
  const ring = (s, em, off, sgn) => O.map(([x, y]) => { const X = x * s, Y = y * s, n = nOf(X, Y); return em.vert([X, Y, zOf(X, Y) + off], sgn > 0 ? n : n.map((v) => -v), [X, Y]); });
  for (let k = 0; k + 1 < scales.length; k++) {
    const em = k === 0 && rimW > 0 ? rim : face;
    const A = ring(scales[k], em, 0, 1), B = ring(scales[k + 1], em, 0, 1);
    for (let i = 0; i < O.length; i++) { const j = (i + 1) % O.length; if (scales[k + 1] > 1e-6) em.quad(A[i], A[j], B[j], B[i]); else em.tri(A[i], A[j], B[i]); }
  }
  // the back: the same surface, `thick` behind, one fan (its planks are the back material's grain)
  const Bk = ring(1, back, -T, -1), cb = back.vert([0, 0, zOf(0, 0) - T], nOf(0, 0).map((v) => -v), [0, 0]);
  for (let i = 0; i < O.length; i++) back.tri(cb, Bk[(i + 1) % O.length], Bk[i]);
  // the edge between them (the rim's, or the face's when it has none)
  for (let i = 0; i < O.length; i++) {
    const [ax, ay] = O[i], [bx, by] = O[(i + 1) % O.length], n = norm([by - ay, -(bx - ax), 0]);
    const q = [[ax, ay, zOf(ax, ay)], [bx, by, zOf(bx, by)], [bx, by, zOf(bx, by) - T], [ax, ay, zOf(ax, ay) - T]].map((v, k) => rim.vert(v, n, [k === 1 || k === 2 ? 1 : 0, v[2]]));
    rim.quad(q[0], q[1], q[2], q[3]);
  }
}

// ---- HULL: a ship's or a boat's hull lofted along +x, the stern at x = 0 and the bow at x = `length` (metres), y up
// from its keel's lowest point (0), z across. Its lines, each a list of [t, value] over t = 0 (stern) .. 1 (bow),
// read by straight interpolation:
//   `sheer` the gunwale's height (default: `depth` amidships, rising a little to the ends),
//   `keel`  the bottom's height (default flat, rising to the posts: a rocker for a longship or a gondola),
//   `plan`  the half-breadth as a share of `beam` / 2 (default a fine-ended hull, fullest amidships; a share > 0 at
//           t = 0 is a transom stern, closed flat),
//   `fullness` the section between (default .5): 0 a sharp V, .3 a round bilge, 1 a flat-bottomed box,
//   `tumblehome` how much the sides lean in above the waterline (a galleon's), negative flaring out (a dory's).
// The skin is a grid of stations by section points, its normals from the surface. And, asked for by name:
//   `deck` [{ y, from, to, material }] flat decks laid where the hull is that high; `rail` r a gunwale rod along
//   both sheer lines; `keelBeam` [w, h] a keel and stem and sternpost proud of the skin; `thwarts` { n, y, w, from, to }
//   benches across an open boat; `ribs` { n, w } frames inside (an open boat's). uv: along the hull (a planked
//   pattern runs fore and aft), down the section.
const lineAt = (line, t) => {
  if (typeof line === "number") return line;
  for (let k = 1; k < line.length; k++) if (t <= line[k][0] + 1e-9) { const f = (t - line[k - 1][0]) / Math.max(1e-9, line[k][0] - line[k - 1][0]); return line[k - 1][1] + (line[k][1] - line[k - 1][1]) * Math.max(0, Math.min(1, f)); }
  return line[line.length - 1][1];
};
function hull(sinkOf, M, p, P) {
  const L = p.length ?? 8, B = p.beam ?? L * .25, D = p.depth ?? B * .45;
  const sheer = p.sheer ?? [[0, D * 1.12], [.5, D], [1, D * 1.2]], keel = p.keel ?? [[0, D * .35], [.12, 0], [.88, 0], [1, D * .4]];
  const plan = p.plan ?? [[0, 0], [.08, .38], [.3, .9], [.55, 1], [.8, .7], [.95, .25], [1, 0]];
  const full = p.fullness ?? .5, tumble = p.tumblehome ?? 0;
  const nS = Math.max(8, Math.round((p.stations ?? 28) * (P.detail ?? 1))), m = Math.max(3, Math.round((p.sides ?? 7) * (P.detail ?? 1)));
  const e = emitter(sinkOf(p.material ?? "planks"), M);
  // a section point: phi 0 at the gunwale .. pi/2 at the keel, on a quarter superellipse of exponent n (1 a V, 2 round, big a box)
  const n = 1 + 4 * Math.max(0, Math.min(1, lineAt(full, .5)));
  const at = (t, s, side) => {   // s: -1 (port gunwale) .. 0 (keel) .. 1 (starboard gunwale)
    const hb = B / 2 * lineAt(plan, t), ky = lineAt(keel, t), sy = lineAt(sheer, t), phi = (1 - Math.abs(s)) * Math.PI / 2;
    const nn = 1 + 4 * Math.max(0, Math.min(1, typeof full === "number" ? full : lineAt(full, t)));
    let w = hb * Math.pow(Math.cos(phi), 2 / nn), y = ky + (sy - ky) * (1 - Math.pow(Math.sin(phi), 2 / nn));
    const up = (y - ky) / Math.max(1e-6, sy - ky);
    if (tumble) w *= 1 - tumble * Math.max(0, up - .55) / .45;
    return [t * L, y, Math.sign(s) * w * (side ?? 1)];
  };
  const grid = [];
  for (let i = 0; i <= nS; i++) {
    const t = i / nS, row = [];
    for (let j = -m; j <= m; j++) row.push(at(t, j / m));
    grid.push(row);
  }
  const nrm = (i, j) => {   // (the tangent along x crossed with the one across, port to starboard: out of the skin)
    const a = grid[Math.min(nS, i + 1)][j + m], b = grid[Math.max(0, i - 1)][j + m], c = grid[i][Math.min(2 * m, j + m + 1)], d = grid[i][Math.max(0, j + m - 1)];
    return norm(cross(sub(a, b), sub(c, d)));
  };
  const ids = grid.map((row, i) => row.map((q, jj) => { const j = jj - m; return e.vert(q, nrm(i, j), [q[0], (j / m) * (lineAt(sheer, i / nS) - lineAt(keel, i / nS)) * 1.3]); }));
  for (let i = 0; i < nS; i++) for (let jj = 0; jj < 2 * m; jj++) e.quad(ids[i][jj], ids[i][jj + 1], ids[i + 1][jj + 1], ids[i + 1][jj]);
  for (const [i, sgn] of [[0, -1], [nS, 1]]) {   // an end that is not a point: closed flat (a transom)
    if (B / 2 * lineAt(plan, i / nS) < .02) continue;
    const c = e.vert([i / nS * L, (lineAt(sheer, i / nS) + lineAt(keel, i / nS)) / 2, 0], [sgn, 0, 0], [0, 0]);
    const ring = grid[i].map((q) => e.vert(q, [sgn, 0, 0], [q[2], q[1]]));
    for (let jj = 0; jj < 2 * m; jj++) e.tri(c, ring[jj], ring[jj + 1]);
  }
  // the half-width of the section at station t at height y (for a deck, a thwart)
  const widthAt = (t, y) => {
    const ky = lineAt(keel, t), sy = lineAt(sheer, t);
    if (y <= ky || y > sy + 1e-6) return 0;
    let lo = 0, hi = 1;
    for (let k = 0; k < 24; k++) { const mid = (lo + hi) / 2; if (at(t, mid)[1] < y) lo = mid; else hi = mid; }
    return at(t, (lo + hi) / 2)[2];
  };
  for (const dk of p.deck ? (Array.isArray(p.deck) ? p.deck : [p.deck]) : []) {   // a flat deck, from..to, planked across the beam
    const ed = emitter(sinkOf(dk.material ?? p.deckMaterial ?? "deck"), M), y = dk.y ?? D * .85, t0 = dk.from ?? 0, t1 = dk.to ?? 1;
    const k = Math.max(2, Math.round(nS * (t1 - t0)));
    for (const up of dk.under === false ? [1] : [1, -1]) {
      const rows = [];
      for (let i = 0; i <= k; i++) { const t = t0 + (t1 - t0) * i / k, w = Math.max(.01, widthAt(t, y)); rows.push([ed.vert([t * L, y, -w], [0, up, 0], [t * L, -w]), ed.vert([t * L, y, w], [0, up, 0], [t * L, w])]); }
      for (let i = 0; i < k; i++) ed.quad(rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]);
    }
  }
  if (p.rail) {   // the gunwale: a round rod along each sheer line
    const er = emitter(sinkOf(p.railMaterial ?? "wood"), M);
    for (const sgn of [-1, 1]) sweep(er, { path: grid.map((row) => row[sgn < 0 ? 0 : 2 * m]), r: p.rail, seg: 1, sides: 6 }, P);
  }
  if (p.keelBeam) {   // the keel with its stem and sternpost: a square section along the bottom line and up the ends
    const [w, h] = p.keelBeam, ek = emitter(sinkOf(p.keelMaterial ?? "wood"), M), path = [];
    for (let i = 0; i <= nS; i++) { const t = i / nS; path.push([t * L, lineAt(keel, t) - h * .5, 0]); }
    const stern = [[0, lineAt(sheer, 0) + (p.postRise ?? 0), 0]], bow = [[L, lineAt(sheer, 1) + (p.postRise ?? 0), 0]];
    sweep(ek, { path: [...stern, ...path, ...bow], section: [w, h], up: [0, 1, 0], seg: 1 }, P);
  }
  if (p.thwarts) {   // benches across an open boat, `n` of them from..to at height y (the half-width there), w wide
    const { n: nT = 3, y = D * .6, w = .2, from = .15, to = .85, thick = .03 } = p.thwarts;
    for (let i = 0; i < nT; i++) {
      const t = nT === 1 ? (from + to) / 2 : from + (to - from) * i / (nT - 1), hw = widthAt(t, y);
      if (hw > .05) box(emitter(sinkOf(p.thwartMaterial ?? "wood"), mul(M, placeM([t * L, y, 0]))), [w, thick, hw * 2 * .98], 0, P);
    }
  }
  if (p.ribs) {   // frames inside the skin: `n` bent timbers, w wide
    const { n: nR = 8, w = .05, from = .08, to = .92 } = p.ribs, er = emitter(sinkOf(p.ribMaterial ?? "wood"), M);
    for (let i = 0; i < nR; i++) {
      const t = from + (to - from) * i / Math.max(1, nR - 1), path = [];
      for (let j = -m; j <= m; j++) { const q = at(t, j / m); path.push([q[0], q[1] + w * .4, q[2] * (1 - .01)]); }
      sweep(er, { path, section: [w, w * .8], up: [0, 1, 0], seg: 1 }, P);
    }
  }
}

// ---- SAIL: a cloth hung between four `corners` [[x, y], ...] in its own plane (x across, y up; three corners make a
// lateen, a crab claw, a spritsail's triangle) -- bilinear between them, bellied `belly` metres out along +z at its
// middle; `battens` n rods across it (a junk's); drawn from both sides (thin cloth). uv: across and down in metres
// (a striped pattern reads as the cloths sewn side by side).
function sail(sinkOf, M, p, P) {
  const C = p.corners ?? [[-1, 0], [1, 0], [1, -2], [-1, -2]];
  const A = C[0], Bc = C[1], Cc = C[2] ?? C[1], Dc = C[3] ?? C[0], belly = p.belly ?? 0;
  const nu = Math.max(2, Math.round((p.seg ?? 6) * (P.detail ?? 1))), nv = Math.max(2, Math.round((p.seg ?? 6) * (P.detail ?? 1)));
  const e = emitter(sinkOf(p.material ?? "cloth"), M);
  const pt = (u, v) => {   // u across (A->B on the head, D->C on the foot), v down (head 0 .. foot 1)
    const hx = A[0] + (Bc[0] - A[0]) * u, hy = A[1] + (Bc[1] - A[1]) * u, fx = Dc[0] + (Cc[0] - Dc[0]) * u, fy = Dc[1] + (Cc[1] - Dc[1]) * u;
    return [hx + (fx - hx) * v, hy + (fy - hy) * v, belly * Math.sin(u * Math.PI) * Math.sin(v * Math.PI)];
  };
  const grid = [];
  for (let j = 0; j <= nv; j++) { const row = []; for (let i = 0; i <= nu; i++) row.push(pt(i / nu, j / nv)); grid.push(row); }
  const ids = grid.map((row, j) => row.map((q, i) => {
    const a = grid[j][Math.min(nu, i + 1)], b = grid[j][Math.max(0, i - 1)], c = grid[Math.min(nv, j + 1)][i], d = grid[Math.max(0, j - 1)][i];
    let nn = norm(cross(sub(a, b), sub(c, d))); if (nn[2] < 0) nn = nn.map((v) => -v);
    return e.vert(q, nn, [q[0], q[1]]);
  }));
  for (let j = 0; j < nv; j++) for (let i = 0; i < nu; i++) e.quad(ids[j][i], ids[j][i + 1], ids[j + 1][i + 1], ids[j + 1][i]);
  if (p.battens) {   // rods across the cloth at even heights, following its belly
    const eb = emitter(sinkOf(p.battenMaterial ?? "wood"), M), k = Math.round(p.battens);
    for (let b = 0; b <= k; b++) {
      const v = b / k, path = [];
      for (let i = 0; i <= nu; i++) { const q = pt(i / nu, v); path.push([q[0], q[1], q[2] + (p.battenR ?? .02)]); }
      sweep(eb, { path, r: p.battenR ?? .02, seg: 1, sides: 5 }, P);
    }
  }
}

// ---- FACE: a low-poly head on the anatomy (face.js), its several materials; the helpers it draws its eyes, brows,
// ears and neck with are the primitives above, each placed by a small frame inside the part's
function face(sinkOf, M, p, P, out = null) {
  const emitFor = (role, at = null, rot = null) => emitter(sinkOf(role), at || rot ? mul(M, placeM([...(at ?? [0, 0, 0]), ...(rot ?? [0, 0, 0])])) : M);
  const prims = {
    lathe: (role, profile, sides, opts, at) => lathe(emitFor(role, at), profile, sides, opts),
    sphere: (role, r, k, c) => { const prof = []; for (let i = 0; i <= Math.max(3, Math.round(k / 2)); i++) { const a = -Math.PI / 2 + i / Math.max(3, Math.round(k / 2)) * Math.PI; prof.push([r * Math.cos(a), r * Math.sin(a)]); }
      lathe(emitFor(role, c), prof, k, { capLo: false, capHi: false }); },
    disc: (role, r, k, c, dir) => lathe(emitter(sinkOf(role), mul(M, alongM(c, dir.map((v) => -v)))), [[0, 0], [r, 0]], k, { capLo: false, capHi: false }),
    sweep: (role, path, section, up) => sweep(emitFor(role), { path, section, up, seg: 2 }, P),
    tube: (role, path, radii) => sweep(emitFor(role), { path, radii, seg: 1, sides: 6 }, P),
    plate: (role, outline, thick, c, sg, yawOut, pitchBack) => plate(emitFor(role, c, [yawOut * sg * -1, 0, pitchBack * sg * 0]), { outline, thick }),
    // a GUIDE LINE (the face's lattice: its rows and columns), kept for the viewer, in the item's frame
    guide: out ? (pts, name) => out.guides.push({ name, pts: pts.map((q) => [M[0] * q[0] + M[1] * q[1] + M[2] * q[2] + M[3], M[4] * q[0] + M[5] * q[1] + M[6] * q[2] + M[7], M[8] * q[0] + M[9] * q[1] + M[10] * q[2] + M[11]]) }) : null,
  };
  const q = { ...p, scale: p.headScale ?? 1 };   // (the head's own size: `scale` on a part is its placement's)
  return p.type === "hair" ? hairGeometry(q, P, emitFor, prims) : faceGeometry(q, P, emitFor, prims);
}

// ---- MATERIALS: a name out of the library (assets/items/materials.json: a pattern, its palette, its scale), a colour
// ("#8e2f35": plain paint), or written out ({ "pattern": "heraldry/quarterly", "palette": ["#b3262a", "#e8e0c8"] }).
// A part names a ROLE ("wood", "blade", "face"); the item's `materials` says what the role is, a component takes its
// parent's roles for its own, and a role nobody names is looked up as a material itself.
export function materialOf(ref, lib, extraParams = null) {
  let m;
  if (isPlain(ref)) m = { ...ref };
  else if (typeof ref === "string" && /^#[0-9a-fA-F]{6}$/.test(ref)) m = { pattern: "materials/paint", palette: [ref, ref, ref, ref] };
  else m = lib[ref] ? { ...lib[ref] } : { pattern: "materials/paint", palette: ["#9a8a70", "#9a8a70", "#9a8a70", "#9a8a70"], missing: ref };
  if (extraParams && m.fit) m.params = { ...(m.params ?? {}), ...extraParams };
  const key = `${m.pattern}|${JSON.stringify(m.palette ?? null)}|${m.scale ?? 1}|${JSON.stringify(m.params ?? null)}`;
  return { key, pattern: m.pattern, palette: m.palette, scale: m.scale ?? 1, params: m.params, side: m.side };
}

// ---- BUILDING ---------------------------------------------------------------------------------------------------------
// def: an item definition (or its path in the bank); bank: path -> definition; lib: the materials library.
//   seed: which one of its kind (its ranges and picks); params: the caller's own; materials: the caller's roles
// -> { name, groups: [{ material, roles, pos, nor, uv, idx }], hold, markers, bounds, params }
export function buildItem(def0, bank, lib, { seed = 1, params = {}, materials = {}, M = I3(), into = null, depth = 0 } = {}) {
  const def = typeof def0 === "string" ? bank.get(def0) : def0;
  if (!def) throw new Error(`items: no definition "${def0}"`);
  if (depth > 8) throw new Error("items: components nested too deep (one using itself?)");
  const flat = flatten(def, bank), r = rng(seed * 7919 + 17);
  const P = paramsOf(flat, params, r);
  // the roles: the definition's own, drawn by the seed where it gives a choice, under the caller's
  // (a pick may stand anywhere in a material: a shield's heraldry picks its division and its tinctures)
  const drawn = (v) => isPlain(v) && Array.isArray(v.pick) ? drawn(v.pick[Math.floor(r() * v.pick.length) % v.pick.length])
                     : isPlain(v) ? Object.fromEntries(Object.entries(v).map(([k, x]) => [k, drawn(x)])) : v;
  const roles = {};
  for (const [k, v] of Object.entries(flat.materials ?? {})) roles[k] = drawn(v);
  // COLOURWAYS: a set of roles that belong together (a collar's gold, lapis and carnelian; its faience blues) -- the
  // `colourway` param names one, else the seed picks one -- over the roles' own, under the caller's
  if (flat.colourways) {
    const names = Object.keys(flat.colourways), cw = typeof P.colourway === "string" && flat.colourways[P.colourway] ? P.colourway : names[Math.floor(r() * names.length) % names.length];
    P.colourway = cw;
    Object.assign(roles, flat.colourways[cw]);
  }
  Object.assign(roles, materials);
  const out = into ?? { groups: new Map(), markers: [], guides: [] };
  const sinkOf = (role, extra = null) => {
    let ref = roles[role] ?? role, guard = 0;
    while (typeof ref === "string" && roles[ref] !== undefined && roles[ref] !== ref && guard++ < 8) ref = roles[ref];   // (a role named after another role)
    const mat = materialOf(ref, lib, extra);
    if (!out.groups.has(mat.key)) out.groups.set(mat.key, { material: mat, roles: new Set(), pos: [], nor: [], uv: [], idx: [] });
    const g = out.groups.get(mat.key); g.roles.add(role);   // (which roles drew into it: heads.js shades a face's lips flat by theirs)
    return g;
  };
  for (const p0 of flat.parts ?? []) {
    if (!passes(p0.when, P)) continue;
    const p = resolvePart(p0, P);
    for (const PM of placementsOf(p, M, P)) {
      if (p.type === "component" || p.use) {
        buildItem(p.use, bank, lib, { seed: seed + (p.seed ?? 0), params: p.params ? deep(p.params, P) : {}, materials: { ...roles, ...(p.materials ?? {}) }, M: PM, into: out, depth: depth + 1 });
        continue;
      }
      if (p.type === "shield") { shield(sinkOf, PM, p, P); continue; }
      if (p.type === "face") { face(sinkOf, PM, p, P, out); continue; }
      if (p.type === "strand" || p.type === "collar" || p.type === "band") {   // JEWELRY on a fit (jewelry.js): several roles, closed solids
        const em = (role) => emitter(sinkOf(role), PM);
        (p.type === "strand" ? strandGeometry : p.type === "collar" ? collarGeometry : bandGeometry)(p, P, em);
        continue;
      }
      if (p.type === "hull" || p.type === "sail" || p.type === "hair" || p.type === "feathers" || p.type === "petals") {   // (several materials of their own; a sail is cloth, hair ribbons and feathers vanes, seen from both sides)
        const sinks = new Set(), sinkAll = (role, extra) => { const g = sinkOf(role, extra); sinks.add(g); return g; };
        const marks = new Map([...out.groups.values()].map((g) => [g, [g.pos.length / 3, g.idx.length]]));
        if (p.type === "hull") hull(sinkAll, PM, p, P); else if (p.type === "sail") sail(sinkAll, PM, p, P);
        else if (p.type === "feathers") feathersGeometry(p, P, (role) => emitter(sinkAll(role), PM));
        else if (p.type === "petals") petalsGeometry(p, P, (role) => emitter(sinkAll(role), PM)); else face(sinkAll, PM, p, P, out);
        if (p.double || p.type === "sail" || p.type === "hair" || p.type === "feathers" || p.type === "petals") for (const sk of sinks) {
          const [v0, i0] = marks.get(sk) ?? [0, 0], v1 = sk.pos.length / 3, i1 = sk.idx.length, off = v1 - v0;
          for (let v = v0; v < v1; v++) { sk.pos.push(sk.pos[v * 3], sk.pos[v * 3 + 1], sk.pos[v * 3 + 2]); sk.nor.push(-sk.nor[v * 3], -sk.nor[v * 3 + 1], -sk.nor[v * 3 + 2]); sk.uv.push(sk.uv[v * 2], sk.uv[v * 2 + 1]); }
          for (let i = i0; i < i1; i += 3) sk.idx.push(sk.idx[i] + off, sk.idx[i + 2] + off, sk.idx[i + 1] + off);
        }
        continue;
      }
      const sk = sinkOf(p.material ?? "wood"), v0 = sk.pos.length / 3, i0 = sk.idx.length;
      const e = emitter(sk, PM);
      switch (p.type) {
        case "lathe": lathe(e, p.profile, p.sides ?? sidesFor(Math.max(...p.profile.map((q) => q[0])), P), { capLo: p.caps !== false, capHi: p.caps !== false, faceted: !!p.faceted }); break;
        case "rod": {
          const from = p.from ?? [0, 0, 0], to = p.to ?? [0, p.length ?? 1, 0], d = sub(to, from), L = Math.hypot(...d);
          const r0 = p.r0 ?? p.r ?? .01, r1 = p.r1 ?? p.r ?? r0;
          lathe(emitter(sinkOf(p.material ?? "wood"), mul(PM, alongM(from, d))), [[r0, 0], [r1, L]], p.sides ?? sidesFor(Math.max(r0, r1), P, 4, 16));
          break;
        }
        case "sphere": {
          const R = p.r ?? .02, k = p.sides ?? sidesFor(R, P, 6, 20), prof = [];
          for (let i = 0; i <= Math.max(3, Math.round(k / 2)); i++) { const a = -Math.PI / 2 + i / Math.max(3, Math.round(k / 2)) * Math.PI; prof.push([R * Math.cos(a), R * Math.sin(a)]); }
          lathe(e, prof, k, { capLo: false, capHi: false });
          break;
        }
        case "box": {   // rounded edges only on a PUFFY soft thing -- a cushion, a pillow (in a fabric, its smallest side a
          // eighth of its largest or more); a plank, a curtain, a coverlet are six faces: a softened edge is invisible and dear in triangles
          const puffy = /^fabrics\//.test(sk.material.pattern ?? "") && Math.min(...p.size) >= .12 * Math.max(...p.size);
          box(e, p.size, puffy ? p.round ?? 0 : 0, P); break;
        }
        case "sweep": sweep(e, p, P); break;
        case "ring": {   // a torus: `r` round, `tube` thick
          const k = Math.max(8, Math.min(24, Math.round((12 + 60 * p.r) * (P.detail ?? 1))));   // (round the ring: 12 a small one, 24 from a 20 cm radius)
          sweep(e, { path: Array.from({ length: k }, (_, i) => [p.r * Math.cos(i / k * Math.PI * 2), 0, p.r * Math.sin(i / k * Math.PI * 2)]), r: p.tube ?? .01, closed: true, seg: 1, sides: p.sides }, P);
          break;
        }
        case "blade": blade(e, p); break;
        case "plate": plate(e, p); break;
        default: throw new Error(`items: no part type "${p.type}"`);
      }
      if (p.double) {   // a thin shell seen from both sides (a cup guard, a canopy, a sail): its back, turned
        const v1 = sk.pos.length / 3, i1 = sk.idx.length, off = v1 - v0;
        for (let v = v0; v < v1; v++) { sk.pos.push(sk.pos[v * 3], sk.pos[v * 3 + 1], sk.pos[v * 3 + 2]); sk.nor.push(-sk.nor[v * 3], -sk.nor[v * 3 + 1], -sk.nor[v * 3 + 2]); sk.uv.push(sk.uv[v * 2], sk.uv[v * 2 + 1]); }
        for (let i = i0; i < i1; i += 3) sk.idx.push(sk.idx[i] + off, sk.idx[i + 2] + off, sk.idx[i + 1] + off);
      }
    }
  }
  for (const mk of flat.markers ?? []) if (passes(mk.when, P)) {
    const m = resolvePart(mk, P);
    for (const PM of placementsOf(m, M)) out.markers.push({ role: m.role, at: [PM[3], PM[7], PM[11]], yaw: Math.atan2(PM[2], PM[0]), data: m.data ?? {} });
  }
  if (into) return into;
  // ---- the result: arrays, bounds, the hold
  const groups = [...out.groups.values()].filter((g) => g.idx.length).map((g) => ({
    material: g.material, roles: g.roles, pos: new Float32Array(g.pos), nor: new Float32Array(g.nor), uv: new Float32Array(g.uv),   // (roles: which drew into it -- heads.js shades the lips flat and the hair as hair by them)
    idx: (g.pos.length / 3 > 65535 ? Uint32Array : Uint16Array).from(g.idx) }));
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  for (const g of groups) for (let i = 0; i < g.pos.length; i += 3) for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], g.pos[i + k]); hi[k] = Math.max(hi[k], g.pos[i + k]); }
  const hold = flat.hold ? deep(flat.hold, P) : null;
  return { name: flat.name ?? String(def0), kind: flat.category ?? null, era: flat.era ?? null, groups, markers: out.markers, guides: out.guides ?? [], bounds: { lo, hi }, hold, params: P,
           tris: groups.reduce((s, g) => s + g.idx.length / 3, 0) };
}

// ---- HOLDING IT --------------------------------------------------------------------------------------------------------
// hold: { grip: [x, y, z] (where the fist closes, in the item's own frame), axis: [...] (the handle's line through the
// fist, pointing out of it on the thumb's side -- toward a sword's point, a spade's blade, an axe's head), face: [...]
// (square to it: which way the edge or the front looks -- a sword's edge, a shield's face), grip2 (the other hand's
// place, for a two-handed hold: a halberd, a longsword, a bow's string), carry: { axis, face } (how it is carried: its
// axis and face in the HAND's frame -- +x forward, +y up, +z to the right; by default upright, the face forward) }
// -> the 3x4 matrix that puts the item into the hand's frame: the grip at the origin, the axis and face where carry says
export function holdMatrix(hold) {
  const h = hold ?? {};
  const g = h.grip ?? [0, 0, 0], ax = norm(h.axis ?? [0, 1, 0]);
  let fc = h.face ?? [1, 0, 0]; fc = norm(sub(fc, ax.map((v) => v * dot(fc, ax))));
  const carry = h.carry ?? {}, cAx = norm(carry.axis ?? [0, 1, 0]);
  let cFc = carry.face ?? [1, 0, 0]; cFc = norm(sub(cFc, cAx.map((v) => v * dot(cFc, cAx))));
  // item frame (fc, ax, fc x ax) -> hand frame (cFc, cAx, cFc x cAx): R = Hand * Item^T
  const i3 = cross(fc, ax), h3 = cross(cFc, cAx);
  const R = [0, 1, 2].map((r) => [0, 1, 2].map((c) => cFc[r] * fc[c] + cAx[r] * ax[c] + h3[r] * i3[c]));
  const t = [0, 1, 2].map((r) => -(R[r][0] * g[0] + R[r][1] * g[1] + R[r][2] * g[2]));
  return [R[0][0], R[0][1], R[0][2], t[0], R[1][0], R[1][1], R[1][2], t[1], R[2][0], R[2][1], R[2][2], t[2]];
}
// an item's groups carried through a matrix (tools.js puts every held item into its hand's frame once, at build)
export function transformGroups(groups, M) {
  return groups.map((g) => {
    const pos = new Float32Array(g.pos.length), nor = new Float32Array(g.nor.length);
    for (let i = 0; i < g.pos.length; i += 3) {
      const x = g.pos[i], y = g.pos[i + 1], z = g.pos[i + 2], a = g.nor[i], b = g.nor[i + 1], c = g.nor[i + 2];
      pos[i] = M[0] * x + M[1] * y + M[2] * z + M[3]; pos[i + 1] = M[4] * x + M[5] * y + M[6] * z + M[7]; pos[i + 2] = M[8] * x + M[9] * y + M[10] * z + M[11];
      nor[i] = M[0] * a + M[1] * b + M[2] * c; nor[i + 1] = M[4] * a + M[5] * b + M[6] * c; nor[i + 2] = M[8] * a + M[9] * b + M[10] * c;
    }
    return { ...g, pos, nor };
  });
}

// ---- KITS: what a kind of person carries (assets/items/kits/*.json) -- LOADOUTS, each with a weight and the item
// in each hand (`main`: the weapon hand, `off`: the other -- a shield), an item path or { "pick": [...] } of them.
// -> { id, main, off }: each "path#variant" (tools.js takes it as it is), the variant 1..kit.variants drawn by the
// seed too -- a watch of a dozen carries a dozen weapons, but only so many distinct meshes
export function pickKit(kit, seed) {
  const r = rng(seed * 104729 + 7), outs = kit.loadouts ?? [], n = kit.variants ?? 4;
  let w = r() * outs.reduce((s, o) => s + (o.weight ?? 1), 0), o = outs[outs.length - 1];
  for (const x of outs) if ((w -= x.weight ?? 1) < 0) { o = x; break; }
  const one = (v) => isPlain(v) && Array.isArray(v.pick) ? one(v.pick[Math.floor(r() * v.pick.length) % v.pick.length]) : v;
  const hand = (v) => { const p = one(v); return p ? `${p}#${1 + Math.floor(r() * n)}` : null; };
  return { id: o?.id ?? null, main: hand(o?.main), off: hand(o?.off) };
}
