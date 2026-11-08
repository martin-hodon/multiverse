// A SCULPTED BODY'S MESHES (2026-11-04): what bodyspec.js describes -- shapes on bones, eyes, a coat -- made into the
// arrays a skinned mesh is drawn from (bodies.js puts them on the GPU). Pure: no three.js (it is tested in Node).
//
//   1. THE FIELD (sculpt.js): every shape blended into the next by its k, each carrying its ATTRIBUTES -- its colour
//      (linear light), its wetness, its fibres (hairMask), whether the coat grows from it, and a weight of one on its
//      bone. They blend as the surface does: where the head melts into the body the colour and the bone weights pass
//      from one to the other across the same width, so a turning head bends the neck smoothly instead of tearing it.
//   2. THE EYES, found ON that surface: from inside the head (`from`) toward `at` until the field crosses zero -- where
//      the head really is, whatever it was blended with -- a socket carved round that point (its hollow in the lid's
//      colour) and an eyeball of its own set into it, `sink` of its radius below the skin. An eye can never float.
//   3. THE MESH: surface nets on the field -- even, closed, no seams -- simplified (quadric error) to each budget, the
//      broad back thinned and the face kept; every vertex put back on the surface, its normal the field's gradient,
//      its attributes the field's where it sits; its four heaviest bones its skin.
//   4. THE COAT, sown on the fine mesh (before it was thinned: the true surface): blue noise -- darts thrown at the
//      surface, each kept only when no quill already stands within a gap of it -- where the coat attribute holds and
//      the coat's rule (its skirt, the rump's drop, the face's rise) allows. Each quill a thin pyramid leaning back, its
//      skin its root's: it rides the body exactly where it stands.
import { field, surfaceNets, simplify, finish, gradient, onSurface, mirrorOf, mirrorMesh, sweepCurve } from "./sculpt.js";
import { hornMesh, finMesh, sweepMesh } from "./sharp.js";

const lin = (c) => (c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4);
export function rgb(c, dflt = "#808080") {
  if (c == null) c = dflt;
  const n = typeof c === "number" ? c : parseInt(String(c).replace("#", ""), 16);
  return [lin(((n >> 16) & 255) / 255), lin(((n >> 8) & 255) / 255), lin((n & 255) / 255)];
}
function rng(seed) {
  let a = (seed >>> 0) || 1;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
// a smooth value noise in 3D (the coat's mottle: a patch a centimetre or two across a shade darker or lighter)
const hash3 = (i, j, k) => { let h = Math.imul(i, 374761393) + Math.imul(j, 668265263) + Math.imul(k, 2147483647); h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
function noise3(x, y, z) {
  const i = Math.floor(x), j = Math.floor(y), k = Math.floor(z), u = x - i, v = y - j, w = z - k;
  const s = (t) => t * t * (3 - 2 * t), a = s(u), b = s(v), c = s(w);
  const L = (p, q, t) => p + (q - p) * t;
  return L(L(L(hash3(i, j, k), hash3(i + 1, j, k), a), L(hash3(i, j + 1, k), hash3(i + 1, j + 1, k), a), b),
           L(L(hash3(i, j, k + 1), hash3(i + 1, j, k + 1), a), L(hash3(i, j + 1, k + 1), hash3(i + 1, j + 1, k + 1), a), b), c);
}
const nrm = (v) => { const l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; };
const crs = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];

// the attribute vector: [r, g, b, wet, hair, coat, ...a weight per bone]
const NA = 6;
// ...and after the bones' weights, how much it is PATTERNED (0 or 1, blended: a pattern fades out where its shape
// blends into a plain one)
const NP = 1;
export const COAT = { gap: .006, len: .026, r: .0028, sides: 3, lean: .7, vary: .25, skirt: -.3, drop: 0, face: .35, rise: 1.15,
                      tip: "#e4d8bc", dark: .3, base: "#3a2c20", hold: .5 };
// a coat seen far off: its quills that much further apart (a third as many), thicker and a little longer
export const COAT_FAR = { gap: 1.75, r: 1.6, len: 1.1 };
export const MOTTLE = { scale: 70, amount: .08 };   // (a body may say its own: `sculpt.mottle` -- { amount: 0 } on a whale, whose vertices lie far further apart than a patch)

// A BODY IN TWO PASSES (2026-11-08): its SHAPE -- the surface sampled, meshed, simplified to its budgets and put back on
// the field, with the coat's quills -- and its DRESS -- what each vertex is painted, wet, haired and patterned, its skin,
// the eyes, the details (horns, fins, feathers) -- laid on that shape where it stands. The shape is the expensive part
// (all of the sampling and the simplifying) and depends on nothing a coat changes, so the coats and the variants of a
// species that share their shapes share ONE shape build (bodies.js keys it on shapeSpec, below), each dressed in a pass
// that only reads the field at the vertices it has. A variant at another SIZE shares it too: the field of a body scaled
// by f is the field scaled by f (every length, its grid cell among them), so its mesh is the shape's scaled by f.
// buildBody is both passes, as it always was.
export function buildBody(body, opts = {}) { return dressBody(body, buildShape(body, opts), opts); }

// the body made ready to mesh or to dress: its shapes with their attributes, the seated ones moved onto the surface,
// the eyes found on it and their sockets carved -- what both passes need, and cheap (no sampling)
function ready(body) {
  const nb = body.bones.length, PO = NA + nb, A = PO + NP, bi = (id) => Math.max(0, body.bones.indexOf(id ?? "body"));
  const attrOf = (p, colour) => {
    const a = new Array(A).fill(0), c = rgb(colour);
    a[0] = c[0]; a[1] = c[1]; a[2] = c[2]; a[3] = p.wet ?? 0; a[4] = p.hair ?? 0; a[5] = p.coat === true ? 1 : +(p.coat ?? 0); a[NA + bi(p.bone)] = 1;   // (coat: a number over 1 -- longer quills there: a porcupine's crest)
    if (p.pat) a[PO] = 1;
    return a;
  };
  const M = body.mesh;
  // where the line from `from` through `to` comes out of the surface F: the point and the surface's normal there
  const surfaceHit = (F, from, to, what) => {
    if (F.dist(from[0], from[1], from[2]) > 0) {   // (it starts outside -- a mark on a part too thin for the grid: the nearest surface to where it was)
      const S = onSurface(F.dist, to, 12);
      return [S, gradient(F.dist, S[0], S[1], S[2])];
    }
    const d = nrm(to.map((v, k) => v - from[k])), far = Math.hypot(...to.map((v, k) => v - from[k])) * 3 + .01;
    let lo = 0, hi = null;
    for (let t = 0; t < far; t += M.cell / 3) if (F.dist(from[0] + d[0] * t, from[1] + d[1] * t, from[2] + d[2] * t) > 0) { hi = t; break; } else lo = t;
    if (hi === null) throw new Error(`${body.name}: ${what}: no surface from ${from} toward ${to}`);
    for (let s = 0; s < 30; s++) { const m = (lo + hi) / 2; if (F.dist(from[0] + d[0] * m, from[1] + d[1] * m, from[2] + d[2] * m) > 0) hi = m; else lo = m; }
    const S = from.map((v, k) => v + d[k] * hi);
    return [S, gradient(F.dist, S[0], S[1], S[2])];
  };
  let prims = body.prims.map((p) => ({ ...p, attr: p.op === "sub" && p.color == null ? null : attrOf(p, p.color),
    // (a SWEEP's skin along its chain and its bands -- sculpt.js: its attributes where along it a point is nearest)
    ...(p.type === "sweep" ? { chainIdx: p.chain?.map((b) => NA + bi(b)), bandsRGB: p.bands?.map(([a, b, c]) => [a, b, rgb(c)]) } : {}) }));
  // ---- the SEATED shapes (an ear): on the surface the others make ----
  if (prims.some((p) => p.seat)) {
    const Fs = field(prims.filter((p) => !p.seat), A);
    prims = prims.map((p) => {
      if (!p.seat || !p.c) return p;
      const [S, n] = surfaceHit(Fs, p.seat.from ?? body.rest[bi(p.bone)], p.c, "a seated shape"), size = Array.isArray(p.r) ? Math.max(...p.r) : p.r;
      return { ...p, c: S.map((v, k) => v + n[k] * size * (p.seat.out ?? .3)) };
    });
  }
  // ---- the eyes: on the surface as it is ----
  const F0 = field(prims, A, { sharp: NA }), eyes = [], sockets = [];
  for (const e of body.eyes ?? []) {
    const [S, n] = surfaceHit(F0, e.from ?? body.rest[bi(e.bone ?? "head")], e.at, "an eye"), r = e.r ?? .005;
    const c = S.map((v, k) => v - n[k] * r * (e.sink ?? .35));
    eyes.push({ c, r, n, bone: bi(e.bone ?? "head"), color: e.color ?? "#0c0806", iris: e.iris ?? null, pupil: e.pupil ?? "round" });
    sockets.push({ type: "sphere", c, r: r * (e.socket ?? 1.2), k: r * .45, op: "sub",
                   attr: e.lid ? attrOf({ bone: e.bone ?? "head", wet: .2 }, e.lid) : null });
  }
  const placed = prims;
  prims = [...prims, ...sockets];
  return { nb, PO, A, bi, M, placed, sockets, prims, eyes, F: field(prims, A, { sharp: NA }) };
}

// THE SHAPE: { cell (the grid it was meshed on: a body at another size scales it by its own cell over this), lods:
// [{ pos, nor, tri, half }] (on the surface, the normals the field's; half: a mirrored LOD's half -- bodyhalf.js), quills:
// [near, far] (the coat, sown on the fine surface; or null), stats }.
// `family`: the paint of the OTHER looks that share this shape (bodies.js: its coats and variants, each paintSpec at
// cell 1) -- its colour boundaries anchored as well as this body's own, so the one mesh draws every coat's edges (a
// bay's black legs and a chestnut's white socks); without it, this body's alone, as before.
export function buildShape(body, { seed = 11, family = null } = {}) {
  const t0 = Date.now(), R = ready(body), { F, A, M, nb } = R;
  // ---- the mesh ----
  // (a body that is its own mirror image -- sculpt.js mirrorOf; mesh.symmetric true or false says outright -- meshed as
  //  its +z half, simplified to half the budget with its midline held in the plane, and reflected: exactly symmetric,
  //  about half the time. The anchors and the focus are each side's at once: the half keeps what either side needs)
  const sym = M.symmetric ?? mirrorOf(F, M.cell).ok;
  const half = surfaceNets(F.dist, F.box, M.cell, { half: sym }), nets = sym ? mirrorMesh(half) : half;
  const t1 = Date.now();
  const lods = [], halves = [], tris = M.tris;
  let prev = half;
  // (its COLOUR BOUNDARIES anchored: a vertex whose paint differs from its neighbours' keeps its place, so the edge of a
  //  muzzle or a sock is still drawn by the coarse mesh -- what lies between is coarsened instead)
  const at = M.anchor !== 0 || M.focus ? netAttrs(F, half, A) : null;
  const flipped = sym ? { pos: half.pos.map((v, i) => (i % 3 === 2 ? -v : v)) } : null;
  const atM = at && sym ? netAttrs(F, flipped, A) : null;   // (the other side's)
  const both = (f) => { const u = f(at); if (atM) { const w = f(atM); for (let i = 0; i < u.length; i++) u[i] = Math.max(u[i], w[i]); } return u; };
  let anchor = M.anchor === 0 ? null : both((a) => paintAnchors(a, half, A, M.cell, M.anchor ?? PAINT_ANCHOR));
  // (...and every other look's that shares this shape: each one's paint read where these vertices are, its boundaries
  //  held as firmly as its own coat would have held them)
  if (anchor && family?.length) for (const look of family) {
    const Fm = field(paintPrims(R, look, M.cell), 3, { sharp: 3 });
    for (const P of sym ? [half, flipped] : [half]) {
      const w = paintAnchors(netAttrs(Fm, P, 3), half, 3, M.cell, M.anchor ?? PAINT_ANCHOR);
      for (let i = 0; i < w.length; i++) if (w[i] > anchor[i]) anchor[i] = w[i];
    }
  }
  // (its FOCUS -- mesh.focus, { bone index: factor }: the face, the paws -- kept finer than the rest, the factor blended
  //  by the bones' own weights so the change of density is as soft as the joint)
  //  and, on the near mesh, no edge there longer than FOCUS_EDGE cells over the factor's square root: a round
  //  silhouette, not a few long straight segments across a gently curved cheek)
  let scale = M.focus ? both((a) => focusScale(a, half, A, M.focus)) : null;
  for (const [li, target] of tris.entries()) {
    const maxEdge = scale && li === 0 ? Float64Array.from(scale, (f) => (f > 1.2 ? M.cell * FOCUS_EDGE / Math.sqrt(f) : 0)) : null;
    prev = simplify(prev, sym ? Math.ceil(target / 2) : target, { anchor, scale, maxEdge });
    if (anchor) anchor = Float64Array.from(prev.src, (v) => anchor[v]);
    if (scale) scale = Float64Array.from(prev.src, (v) => scale[v]);
    const mm = sym ? mirrorMesh(prev) : prev, L = finish(F, mm, 0);
    lods.push({ pos: L.pos, nor: L.nor, tri: L.tri, half: sym ? { n: prev.mid.length, t: prev.tri.length / 3, twin: mm.twin } : null });   // (bodies.js draws the half twice: halfdraw)
  }
  const t2 = Date.now();
  // ---- the coat, sown on the fine surface ----
  const coat = body.coat ? { ...COAT, ...body.coat } : null;
  const sow = coat ? (C, sd) => sowCoat(F, nets, A, nb, C, sd) : null;
  const quills = coat ? [sow(coat, seed), sow({ ...coat, gap: coat.gap * COAT_FAR.gap, r: coat.r * COAT_FAR.r, len: coat.len * COAT_FAR.len }, seed + 1)] : [null, null];
  return { cell: M.cell, lods, quills, stats: { nets: nets.tri.length / 3, symmetric: sym, looks: 1 + (family?.length ?? 0),
                                                 ms: { nets: t1 - t0, simplify: t2 - t1, shape: Date.now() - t0 } } };
}
// another look's paint on this body's shapes (for its anchors): each field shape in that look's colour, its own paints,
// its eyes' lids -- colour only (three attributes, blended as the body's paint is)
function paintPrims(R, look, cell) {
  const out = [], col = (p, c) => ({ ...p, attr: p.op === "sub" && c == null ? null : rgb(c) });
  let j = 0;
  for (const p of R.placed) if (p.op !== "paint") out.push(col(p, look.colors[j++]));
  for (const p of look.paints) out.push(col(scaleLen(p, cell), p.color));
  R.sockets.forEach((s, i) => out.push({ ...s, attr: look.lids[i] != null ? rgb(look.lids[i]) : null }));
  return out;
}

// THE DRESS: the shape (buildShape; built for this body or another look of it, at its own size) painted as this body
// is -- every vertex's attributes read from this body's field where it stands, then the eyes, the details, the coat and
// the patterns as buildBody always laid them. Cheap: no sampling, no simplifying.
export function dressBody(body, shape, { seed = 11 } = {}) {
  const t0 = Date.now(), R = ready(body), { F, A, nb, PO, bi, M, eyes } = R, f = M.cell / shape.cell;
  PAT_S = body.patScale ?? 1;
  const sc = (a) => (Math.abs(f - 1) < 1e-12 ? a : a.map((v) => v * f));
  const lods = shape.lods.map((L) => {
    const pos = sc(L.pos), nv = pos.length / 3, attr = new Float32Array(nv * A), tmp = new Float64Array(A);
    for (let v = 0; v < nv; v++) { tmp.fill(0); F.at(pos[3 * v], pos[3 * v + 1], pos[3 * v + 2], tmp); attr.set(tmp, v * A); }
    return { pos, nor: L.nor, attr, tri: L.tri };
  });
  const coats = shape.quills.map((q) => q && (Math.abs(f - 1) < 1e-12 ? q : { ...q, pos: sc(q.pos), uv: q.uv.map((v, i) => (i % 2 ? v * f : v)) }));
  const pats = R.prims.some((p) => p.pat) || (body.details ?? []).some((p) => p.pat && p.type !== "feathers");
  const shade = body.shade ? shadeSpec(body.shade, body.prims) : null;
  const MO = { ...MOTTLE, ...(body.mottle ?? {}) };
  const fairCtx = (body.details ?? []).some((q) => q.fair || q.type === "sweep") ? fairContext(F, A, nb, M.cell, shade, MO) : null;
  const out = lods.map((m, li) => assemble(m, A, nb, eyes, coats[Math.min(li, 1)], li, body.details ?? [], pats ? F : null, bi, PO, shade, MO, fairCtx));
  // (a mirrored LOD says where its half is: its first n vertices (the midline's among them, twin[v] === v) and first t
  //  triangles; the rest of its surface are their reflections, twin[] pairing them)
  out.forEach((o, li) => { if (shape.lods[li].half) o.half = shape.lods[li].half; });
  const ms = { ...shape.stats.ms, dress: Date.now() - t0 };
  ms.all = (ms.shape ?? 0) + ms.dress;
  return { lods: out, nb, stats: { nets: shape.stats.nets, tris: out.map((o) => o.index.length / 3), quills: coats.map((c) => (c ? c.n : 0)),
                                   ms, symmetric: shape.stats.symmetric, scaled: Math.abs(f - 1) < 1e-12 ? 1 : f } };
}

// ---- what a shape build depends on (bodies.js keys the shape on it) -----------------------------------------------
// The lengths of a body: every number under these keys (and in their arrays and objects) is metres. A body scaled by f
// has each of them f times over, its cell among them -- so measured in cells they are the same, and the two share a
// shape. (A key missed here only costs sharing: two sizes then never match.)
const LEN = new Set(["c", "r", "a", "b", "ra", "rb", "pts", "k", "kc", "round", "rmin", "rmax", "amp", "size", "from", "at", "rest", "gap", "len", "knots", "cut", "shrink", "bandEdge"]);
// what a body's PAINT is, never its shape: its colours, wetness, fibres, patterns and their frames, the eyes' looks
const PAINT = new Set(["color", "wet", "hair", "pat", "patFrame", "animalFrame", "_frame", "id", "part", "mirror", "iris", "pupil", "lid", "tip", "tipAt", "fleece", "bands"]);
// a copy with every length times f (and the rest as it is)
export function scaleLen(v, f, len = false) {
  if (typeof v === "number") return len ? v * f : v;
  if (Array.isArray(v)) return v.map((x) => scaleLen(x, f, len));
  if (!v || typeof v !== "object") return v;
  const o = {};
  for (const [k, x] of Object.entries(v)) o[k] = scaleLen(x, f, len || LEN.has(k));
  return o;
}
// numbers as a key compares them: lengths to a ten-thousandth of a cell, the rest to seven figures
const canon = (v, u, len = false) => {
  if (typeof v === "number") return len ? Math.round(v * u * 1e4) / 1e4 : +v.toPrecision(7);
  if (Array.isArray(v)) return v.map((x) => canon(x, u, len));
  if (!v || typeof v !== "object") return v;
  const o = {};
  for (const k of Object.keys(v).sort()) if (v[k] !== undefined && !PAINT.has(k)) o[k] = canon(v[k], u, len || LEN.has(k));
  return o;
};
// THE SHAPE'S SPEC: everything the shape build reads, lengths in cells -- equal for two bodies exactly when one's shape
// build serves the other (scaled by their cells): the field's shapes (not their paint, not the paints), the eyes'
// places (their sockets are carved), the bones (their weights are the skin), the rest pose (where a seat or an eye looks
// from), the mesh's budgets and the coat (its quills are sown with the shape). Not the details, the shade, the mottle,
// the patterns: the dress lays those.
export function shapeSpec(body) {
  const u = 1 / body.mesh.cell, { cell, far, ...mesh } = body.mesh;
  return { prims: body.prims.filter((p) => p.op !== "paint").map((p) => canon(p, u)), eyes: (body.eyes ?? []).map((e) => canon(e, u)),
           bones: body.bones, rest: canon(body.rest, u, true), mesh: canon(mesh, u), coat: body.coat ? { ...canon(body.coat, u), colours: [body.coat.tip, body.coat.base, body.coat.darkTip, body.coat.bands] } : null };
}
// A LOOK'S PAINT as the anchors read it, lengths in cells: its field shapes' colours in order, its paints (op "paint"),
// its eyes' lids. null when its paints are not all at the end (they are, as bodyspec.js orders them): then it is its own
export function paintSpec(body) {
  const P = body.prims, first = P.findIndex((p) => p.op === "paint");
  if (first >= 0 && P.slice(first).some((p) => p.op !== "paint")) return null;
  return { colors: P.filter((p) => p.op !== "paint").map((p) => p.color ?? null), paints: P.filter((p) => p.op === "paint").map((p) => scaleLen(p, 1 / body.mesh.cell)),
           lids: (body.eyes ?? []).map((e) => e.lid ?? null) };
}

// COUNTERSHADING (the overlay's `shade`, bodyspec.js): the painted colour crossfaded from the back's tone on top to the
// belly's below, by height in the rest pose along `up` from the root joint -- a smoothstep `k` either side of `at`.
// "mul" scales every vertex by tone / on (the coat colour becomes the tone exactly; a black mark stays black, a white
// one takes the tone's lightness), "mix" replaces only paint near `on` (markings untouched)
function shadeSpec(S, prims) {
  let on = S.on;
  if (on == null) {   // (the coat's colour: the one the most volume is painted in)
    const vol = new Map();
    for (const p of prims) if (p.op !== "sub" && p.op !== "paint" && p.color != null) vol.set(p.color, (vol.get(p.color) ?? 0) + (p.rmax ?? .05) ** 3);
    on = [...vol].sort((x, y) => y[1] - x[1])[0]?.[0] ?? "#808080";
  }
  const up = nrm(S.up ?? [0, 1, 0]);
  const O = rgb(on), tone = (c) => (typeof c === "number" && c < 4 ? O.map((x) => x * c) : rgb(c ?? on));   // (a number under 4: that factor of the coat's colour -- a coat variant keeps its own hue)
  return { back: tone(S.back), belly: tone(S.belly), on: O, o: S.o ?? [0, 0, 0], up, at: S.at ?? 0,
           k: Math.max(1e-3, S.k ?? (S.r ?? .28) * .5), mix: S.mode === "mix", amount: S.amount ?? 1, tol: S.tol ?? .25,
           low: S.low != null ? tone(S.low) : null, lowAt: S.lowAt ?? -(S.r ?? .28) * 1.3 };
}
function shadeOf(S, x, y, z, c) {
  const h = (x - S.o[0]) * S.up[0] + (y - S.o[1]) * S.up[1] + (z - S.o[2]) * S.up[2] - S.at;
  let t = Math.min(1, Math.max(0, .5 + .5 * h / S.k)); t = t * t * (3 - 2 * t);
  // (and below the belly -- the legs -- to `low`, if it says: a pale belly over legs of the coat's own colour)
  let u = 0;
  if (S.low) { u = Math.min(1, Math.max(0, .5 - .5 * (h + S.at - S.lowAt) / S.k)); u = u * u * (3 - 2 * u); }
  const T = (i) => (S.belly[i] + (S.back[i] - S.belly[i]) * t) * (1 - u) + (S.low ? S.low[i] * u : 0);
  if (S.mix) {
    const d = Math.hypot(c[0] - S.on[0], c[1] - S.on[1], c[2] - S.on[2]), near = S.amount * (1 - Math.min(1, d / S.tol));
    for (let i = 0; i < 3; i++) c[i] += (T(i) - c[i]) * near;
  } else {
    for (let i = 0; i < 3; i++) c[i] = Math.min(1, c[i] * T(i) / Math.max(1e-4, S.on[i]));
  }
}

// how firmly a vertex on a colour boundary is held (against the quadric's area-weighted squared distances: a cell's
// area, times the contrast in linear rgb to its most different neighbour, times this)
export const PAINT_ANCHOR = 40;
export const FOCUS_EDGE = 6;
// the field's attributes at every vertex of the fine mesh (once: the anchors and the focus both read them)
function netAttrs(F, nets, A) {
  const nv = nets.pos.length / 3, out = new Float32Array(nv * A), tmp = new Float64Array(A);
  for (let v = 0; v < nv; v++) { tmp.fill(0); F.at(nets.pos[3 * v], nets.pos[3 * v + 1], nets.pos[3 * v + 2], tmp); out.set(tmp, v * A); }
  return out;
}
function paintAnchors(at, nets, A, cell, k) {
  const nv = nets.pos.length / 3, col = new Float32Array(nv * 3);
  for (let v = 0; v < nv; v++) { col[3 * v] = at[v * A]; col[3 * v + 1] = at[v * A + 1]; col[3 * v + 2] = at[v * A + 2]; }
  const c = new Float32Array(nv), T = nets.tri;
  for (let f = 0; f < T.length; f += 3) for (let e = 0; e < 3; e++) {
    const a = T[f + e], b = T[f + (e + 1) % 3];
    const d = Math.hypot(col[3 * a] - col[3 * b], col[3 * a + 1] - col[3 * b + 1], col[3 * a + 2] - col[3 * b + 2]);
    if (d > c[a]) c[a] = d; if (d > c[b]) c[b] = d;
  }
  const w = new Float64Array(nv);
  for (let v = 0; v < nv; v++) if (c[v] > .03) w[v] = k * c[v] * cell * cell;
  return w;
}

function focusScale(at, nets, A, focus) {
  const nv = nets.pos.length / 3, s = new Float64Array(nv), fs = Object.entries(focus).map(([b, f]) => [NA + +b, f]);
  for (let v = 0; v < nv; v++) {
    const o = v * A;
    let tot = 0, f = 0;
    for (let b = NA; b < A - NP; b++) tot += at[o + b];
    for (const [b, k] of fs) f += at[o + b] * (k - 1);
    s[v] = 1 + (tot > 0 ? f / tot : 0);
  }
  return s;
}

// a vertex's four heaviest bones, their weights summing to one
function top4(w, nb, outI, outW, o) {
  const idx = [0, 1, 2, 3].map(() => 0), wt = [0, 0, 0, 0];
  for (let b = 0; b < nb; b++) {
    const v = w[b];
    if (v <= wt[3]) continue;
    let k = 3;
    while (k > 0 && wt[k - 1] < v) { wt[k] = wt[k - 1]; idx[k] = idx[k - 1]; k--; }
    wt[k] = v; idx[k] = b;
  }
  const s = wt[0] + wt[1] + wt[2] + wt[3] || 1;
  for (let k = 0; k < 4; k++) { outI[o + k] = idx[k]; outW[o + k] = wt[k] / s; }
}

// A PATTERN'S FRAME (bodies.js paints the composite's patternAt per pixel): the point in the frame of the shape it is
// nearest -- along its axis from its first end, as the composite's partLocal measures it -- and that shape's radius.
// The solid patterns (a giraffe's cells, a cow's blotches, scales, scutes, a leopard's patches) are laid in the rest
// pose's own space instead: they run on across the seams between shapes, where a part's frame would break them.
const SOLID = new Set([5, 7, 17, 18, 21, 22, 25, 27, 28, 29, 32, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 63, 64, 65]);
// the COAT patterns (coatpat.js paints them): laid at the body's own size (body.patScale -- a leopard's rosettes, a
// cub's stripes: the same number on a smaller coat), where the rest keep the composite's metres
export const COAT_PATS = new Set([3, 4, 5, 18, 21, 22, 26, 35, 63]);
function frameOf(p) {
  let o, u;
  if (p.type === "cone") { o = p.a; u = nrm(p.b.map((v, k) => v - p.a[k])); }
  else if (p.type === "tube" || p.type === "sweep") { o = p.pts[0].slice(0, 3); u = nrm(p.pts[p.pts.length - 1].slice(0, 3).map((v, k) => v - o[k])); }
  else if (p.type === "tri") { o = p.a; u = nrm(p.b.map((v, k) => v - p.a[k])); }
  else if (p.type === "ell" && p.axes) { o = p.c; u = p.axes[p.r.indexOf(Math.max(...p.r))]; }
  else if (p.type === "horn") { o = p.pts[0].slice(0, 3); u = nrm(p.pts[p.pts.length - 1].slice(0, 3).map((v, k) => v - o[k])); }
  else if (p.type === "fin") { o = p.root[0].slice(0, 3); u = nrm(p.root[p.root.length - 1].slice(0, 3).map((v, k) => v - o[k])); }
  else { o = p.c ?? [0, 0, 0]; u = [1, 0, 0]; }
  let ref = Math.abs(u[1]) < .9 ? [0, 1, 0] : [1, 0, 0], w = nrm(crs(ref, u)), v = crs(u, w);   // (banner_wgsl partLocal's frame)
  // (a LIMB -- its axis near the vertical, off the middle -- measures round from its OUTER side, so a stripe that wraps
  //  only part way round it is on the outside of the leg, where a tiger's are)
  const cz = p.type === "cone" ? (p.a[2] + p.b[2]) / 2 : p.type === "tube" || p.type === "sweep" ? o[2] : p.c?.[2] ?? 0;
  if (Math.abs(u[1]) > .7 && Math.abs(cz) > 1e-3) {
    const side = [0, 0, Math.sign(cz)], d = u[2] * side[2];
    v = nrm([-u[0] * d, -u[1] * d, side[2] - u[2] * d]); w = crs(u, v);
  }
  const r = p.type === "cone" ? (p.ra + p.rb) / 2 : p.type === "tube" || p.type === "horn" || p.type === "sweep" ? p.pts.reduce((s, q) => s + q[3], 0) / p.pts.length
          : p.type === "fin" ? p.thick ?? .02
          : p.type === "ell" ? Math.min(...p.r) : p.r ?? .05;
  return { o, u, v, w, r };
}
// the frame a shape's pattern is laid in: its own (above); the animal's (`animalFrame`: shell.js bodyFrame -- along its
// root, up, across); or, for the solid patterns, the rest pose's space itself
function patFrame(p) {
  if (p.patFrame) { const { o, u, v, r } = p.patFrame; return { o, u, v, w: crs(u, v), r }; }   // (authored: bodyspec.js placeShape)
  const F = frameOf(p);
  if (p.animalFrame) { const { o, u, r } = p.animalFrame; return { o, u, v: [0, 1, 0], w: [u[2], 0, -u[0]], r: r ?? F.r }; }
  if (SOLID.has(p.pat)) return { o: [0, 0, 0], u: [1, 0, 0], v: [0, 1, 0], w: [0, 0, 1], r: F.r };
  return F;
}
const dot3 = (q, a) => q[0] * a[0] + q[1] * a[1] + q[2] * a[2];
// a point in a shape's pattern frame, written to the k-th of a vertex's three slots (patP, patQ, patR)
let PAT_S = 1;   // (the body's pattern scale while it is assembled: buildBody sets it)
function patternOf(p, x, y, z, out, o, k = 0) {
  const F = p._frame ?? (p._frame = patFrame(p)), S = COAT_PATS.has(p.pat) ? PAT_S : 1;
  out.id[3 * o + k] = p.pat;
  if (p.type === "sweep" && !p.animalFrame && !SOLID.has(p.pat)) {   // (a SWEEP's own frame BENT along it: sweepFrame)
    const [a, b, c] = sweepFrame(p, F, x, y, z);
    (k === 2 ? out.r : k ? out.q : out.p).set([a / S, b / S, c / S, F.r / S], 4 * o);
    return;
  }
  const q = [x - F.o[0], y - F.o[1], z - F.o[2]];
  (k === 2 ? out.r : k ? out.q : out.p).set([dot3(q, F.u) / S, dot3(q, F.v) / S, dot3(q, F.w) / S, F.r / S], 4 * o);
}
// A SWEEP's pattern frame follows its curve: "along" is the arc length (from where its start lies along the frame's own
// axis), "round" is measured from the frame's v carried along the curve without twisting -- a ringed or striped tail
// that curls keeps its rings square to it, where a straight frame cut them slantwise across the bend
function sweepFrame(p, F, x, y, z) {
  if (!p._curve) {
    const C = sweepCurve(p), U0 = C.U[0], T0 = C.T[0], W0 = crs(T0, U0), d = dot3(F.v, T0), vp = [F.v[0] - T0[0] * d, F.v[1] - T0[1] * d, F.v[2] - T0[2] * d];
    p._curve = { C, phi: Math.atan2(dot3(vp, W0), dot3(vp, U0)), s0: dot3([C.X[0][0] - F.o[0], C.X[0][1] - F.o[1], C.X[0][2] - F.o[2]], F.u) };
  }
  const { C, phi, s0 } = p._curve, { X, S, T, U, m } = C;
  let best = Infinity, bi = 0, bt = 0;
  for (let i = 0; i + 1 < m; i++) {
    const A = X[i], B = X[i + 1], e0 = B[0] - A[0], e1 = B[1] - A[1], e2 = B[2] - A[2], l2 = e0 * e0 + e1 * e1 + e2 * e2 || 1e-18;
    const t = Math.max(0, Math.min(1, ((x - A[0]) * e0 + (y - A[1]) * e1 + (z - A[2]) * e2) / l2));
    const d = (x - A[0] - e0 * t) ** 2 + (y - A[1] - e1 * t) ** 2 + (z - A[2] - e2 * t) ** 2;
    if (d < best) { best = d; bi = i; bt = t; }
  }
  const i = bi, t = bt, l = (a, b) => [0, 1, 2].map((k) => a[k] + (b[k] - a[k]) * t);
  const c = l(X[i], X[i + 1]), Tn = nrm(l(T[i], T[i + 1])), Un = nrm(l(U[i], U[i + 1])), Wn = crs(Tn, Un);
  const V = [0, 1, 2].map((k) => Un[k] * Math.cos(phi) + Wn[k] * Math.sin(phi)), W = crs(Tn, V), q = [x - c[0], y - c[1], z - c[2]];
  return [s0 + S[i] + (S[i + 1] - S[i]) * t, dot3(q, V), dot3(q, W)];
}
// the solid patterns whose lattice scales with the shape's r (scales, osteoderms, the sea's spots, mottle, row scales):
// two shapes of different girths in the rest pose's space disagree everywhere, so they are two groups (patternGroups)
const SIZED = new Set([17, 25, 27, 28, 29, 32]);
// (shapes that share a frame -- the animal's, or the rest pose's space -- need no crossfade between them)
const frameKey = (p) => p.animalFrame ?? p.patFrame ?? (SOLID.has(p.pat) ? SOLID : p);
// the groups of a body's patterned shapes: by frame and pattern, in the order they first come
function patternGroups(patterned) {
  const keys = [], of = patterned.map((q) => {
    // (and by SIZE: a shared frame's lattice is laid from its origin at the shape's own size, so two shapes of different
    //  sizes in it -- a trunk in tubes of falling girth -- disagree everywhere and must crossfade like two frames, or
    //  the size steps from vertex to vertex at their seam and garbles it: the whale shark's spots)
    //  (only a pattern whose lattice is laid AT that size: the rest -- a giraffe's cells, piebald, agouti, a lynx's spots
    //  -- paint the same at any r, and splitting them by it only crowded the third pattern at a seam out of the two slots)
    const k = frameKey(q.src), fr = (q.src._frame ?? patFrame(q.src)).r, r = !SIZED.has(q.src.pat) ? "" : JSON.stringify(Array.isArray(fr) ? fr.map((x) => +(+x).toFixed(4)) : +(+fr).toFixed(4));   // (a box's r is its three half-sizes)
    let g = keys.findIndex((e) => e.k === k && e.pat === q.src.pat && e.r === r);
    if (g < 0) { g = keys.length; keys.push({ k, pat: q.src.pat, r }); }
    return g;
  });
  patterned.groups = { of, d: new Float64Array(keys.length), s: new Int32Array(keys.length) };
  return patterned;
}
// A MESH'S PATTERN SLOTS (2026-11-08), every vertex's at once. The frame coordinates are interpolated across each
// triangle, so a slot must hold the SAME group at all three corners wherever it carries weight at any of them: a slot
// holding the head's frame at one corner and the neck's at the next paints, between them, a point in neither -- the
// stripes squeezed into the nested terraces a zebra's forehead showed. Choosing each vertex's pair by its own nearest
// two groups (in group order) broke that wherever the nearest group's IDLE partner changed (the cranium in slot 1
// beside a vertex whose idle second group came after it, in slot 0 beside one whose came before), and a vertex with no
// pattern (a hoof, a muzzle) carried zeros into the triangles on its edge. So:
//  (1) each vertex's ACTIVE groups: its nearest, and up to two more where the crossfade gives them a share (each
//      group's odds t / (1 - t) against the nearest, t the two-group crossfade -- so two groups blend as they always did);
//  (2) each vertex NEEDS every group active at a corner of a triangle it is in -- painted in that group's frame even
//      where its own share is nil;
//  (3) a first choice of slots, mesh-wide: each group one slot of its own, coloured like a map (DSatur: the most
//      constrained group first) so groups needed together sit in different slots; a vertex holds each group it needs
//      in that group's slot, and fills a slot it has no use for with its nearest group (weight nil);
//  (4) then each vertex in turn takes whichever arrangement of what it needs tears the fewest of its triangles (a slot
//      torn: different groups at its corners, weighted by the most that slot carries there), until none improves; and
//      a region holding one arrangement tries every order of its slots at once.
// THREE slots (2026-11-08): where three frames meet -- a cat's cheek, skull and neck below its ear -- two slots tore a
// triangle at every vertex of the junction and drew it as a stair-stepped line. Only where four groups meet within one
// triangle is a slot still torn.
const NS = 3;
const PERMS = [[0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];   // (every other order of the three slots)
function patternsMesh(patterned, P, tri, nv, K, out) {
  const G = patterned.groups, NG = G.d.length, dg = G.d, sh = G.s, n = patterned.length;
  // (1) the active groups, nearest first: ag (-1 none), their nearest shapes (as) and shares (aw)
  const ag = new Int32Array(nv * NS).fill(-1), as = new Int32Array(nv * NS), aw = new Float32Array(nv * NS), ord = [];
  for (let v = 0; v < nv; v++) {
    if (K[v] < 1e-3) continue;
    const x = P[3 * v], y = P[3 * v + 1], z = P[3 * v + 2];
    dg.fill(Infinity);
    for (let i = 0; i < n; i++) { const d = patterned[i].d(x, y, z), g = G.of[i]; if (d < dg[g]) { dg[g] = d; sh[g] = i; } }
    ord.length = 0;
    for (let g = 0; g < NG; g++) if (dg[g] < Infinity) ord.push(g);
    if (!ord.length) continue;
    ord.sort((a, b) => dg[a] - dg[b] || a - b);
    const a = ord[0];
    let m = 1, sum = 1;
    ag[v * NS] = a; as[v * NS] = sh[a]; aw[v * NS] = 1;
    for (let j = 1; j < ord.length && m < NS; j++) {
      const b = ord[j], band = Math.max(patterned[sh[a]].k, patterned[sh[b]].k, 1e-4), t = Math.min(1, Math.max(0, .5 - .5 * (dg[b] - dg[a]) / band));
      if (t <= 1e-4) continue;
      const o = t / (1 - t);
      ag[v * NS + m] = b; as[v * NS + m] = sh[b]; aw[v * NS + m] = o; sum += o; m++;
    }
    for (let j = 0; j < m; j++) aw[v * NS + j] /= sum;
  }
  const mineOf = (v) => { const M = []; for (let j = 0; j < NS; j++) if (ag[v * NS + j] >= 0) M.push(ag[v * NS + j]); return M; };
  const own = (v, g) => { for (let j = 0; j < NS; j++) if (ag[v * NS + j] === g) return aw[v * NS + j]; return 0; };
  // (2) what each vertex needs, its neighbours, and the triangles it is in
  const need = Array.from({ length: nv }, () => null), nbr = Array.from({ length: nv }, () => []), tris = Array.from({ length: nv }, () => []), U = [];
  for (let f = 0; f < tri.length; f += 3) {
    U.length = 0;
    for (let c = 0; c < 3; c++) { const v = tri[f + c]; for (let j = 0; j < NS; j++) { const g = ag[v * NS + j]; if (g >= 0 && !U.includes(g)) U.push(g); } }
    if (!U.length) continue;
    for (let c = 0; c < 3; c++) {
      const v = tri[f + c], L = need[v] ?? (need[v] = []);
      for (const g of U) if (!L.includes(g)) L.push(g);
      nbr[v].push(tri[f + (c + 1) % 3], tri[f + (c + 2) % 3]); tris[v].push(f);
    }
  }
  // a vertex's ARRANGEMENT: [slot 0's group, slot 1's, slot 2's, and the shares in them] -- each group it paints
  // itself with its share in one slot holding it; one with no share of its own whole in one slot
  const cand = (v) => {   // (every arrangement that keeps what it paints itself)
    const L = need[v], mine = mineOf(v), C = [];
    const pool = [...mine, ...L.filter((g) => !mine.includes(g))].slice(0, Math.max(mine.length, 5));
    for (const a of pool) for (const b of pool) for (const c of pool) {
      const gs = [a, b, c];
      if (!mine.every((g) => gs.includes(g))) continue;
      if (mine.length) {   // (its shares, each in any one slot holding that group)
        const opts = mine.map((g) => [0, 1, 2].filter((k) => gs[k] === g));
        const go = (i, w) => {
          if (i === mine.length) { C.push([a, b, c, ...w]); return; }
          for (const k of opts[i]) { const w2 = w.slice(); w2[k] = own(v, mine[i]); go(i + 1, w2); }
        };
        go(0, [0, 0, 0]);
      } else for (let k = 0; k < NS; k++) C.push([a, b, c, k === 0 ? 1 : 0, k === 1 ? 1 : 0, k === 2 ? 1 : 0]);   // (no share of its own: its neighbours')
    }
    return C;
  };
  // (3) the first choice: a SLOT PER GROUP, mesh-wide -- groups that meet (are needed together at a vertex) in
  //  different slots, coloured most-constrained first (DSatur), each its least-clashing slot. Where the groups that
  //  meet can be so coloured -- any junction of three, a chain of them -- no triangle tears at all; a clash (four that
  //  meet together) is left to the local search.
  const meet = Array.from({ length: NG }, () => new Map());
  for (let v = 0; v < nv; v++) {
    const L = need[v];
    if (L) for (let i = 0; i < L.length; i++) for (let j = i + 1; j < L.length; j++) {
      meet[L[i]].set(L[j], (meet[L[i]].get(L[j]) ?? 0) + 1); meet[L[j]].set(L[i], (meet[L[j]].get(L[i]) ?? 0) + 1);
    }
  }
  const slot = new Int32Array(NG).fill(-1);
  for (let left = NG; left > 0; left--) {
    let g = -1, gs = -1, gd = -1;
    for (let h = 0; h < NG; h++) {
      if (slot[h] >= 0) continue;
      const seen = new Set(); let dsum = 0;
      for (const [e, w] of meet[h]) { if (slot[e] >= 0) seen.add(slot[e]); dsum += w; }
      if (seen.size > gs || (seen.size === gs && dsum > gd)) { g = h; gs = seen.size; gd = dsum; }
    }
    const cost = [0, 0, 0];
    for (const [e, w] of meet[g]) if (slot[e] >= 0) cost[slot[e]] += w;
    let k = 0;
    for (let j = 1; j < NS; j++) if (cost[j] < cost[k]) k = j;
    slot[g] = k;
  }
  const cfg = new Array(nv).fill(null);
  for (let v = 0; v < nv; v++) {
    const L = need[v];
    if (!L) continue;
    const mine = mineOf(v), gs = [-1, -1, -1];
    for (const g of mine) { let k = slot[g]; if (gs[k] >= 0) { k = gs.indexOf(-1); } gs[k] = g; }   // (its own it must hold: in another slot if its own is taken)
    for (const g of L) if (!mine.includes(g) && gs[slot[g]] < 0) gs[slot[g]] = g;
    const fill = mine[0] ?? L[0], c = [0, 0, 0, 0, 0, 0];
    for (let k = 0; k < NS; k++) { c[k] = gs[k] >= 0 ? gs[k] : fill; c[NS + k] = gs[k] >= 0 ? own(v, gs[k]) : 0; }
    if (!mine.length) { let k = 0; for (let j = 0; j < NS; j++) if (c[j] === L[0]) { k = j; break; } c[NS + k] = 1; }   // (no share of its own: whole in its first need's slot)
    cfg[v] = c;
  }
  // (4) the local search: the arrangement that tears least where its triangles carry weight
  const torn = (f, v, c) => {
    const q0 = tri[f] === v ? c : cfg[tri[f]], q1 = tri[f + 1] === v ? c : cfg[tri[f + 1]], q2 = tri[f + 2] === v ? c : cfg[tri[f + 2]];
    if (!q0 || !q1 || !q2) return 0;
    const kx = Math.min(1, Math.max(K[tri[f]], K[tri[f + 1]], K[tri[f + 2]]));
    let t = 0;
    for (let k = 0; k < NS; k++) if (q0[k] !== q1[k] || q1[k] !== q2[k]) t += kx * Math.max(q0[NS + k], q1[NS + k], q2[NS + k]);
    return t;
  };
  const single = () => {
    let any = false;
    for (let pass = 0, moved = true; moved && pass < 12; pass++) {
      moved = false;
      for (let v = 0; v < nv; v++) {
        if (!need[v]) continue;
        const here = (c) => tris[v].reduce((t, f) => t + torn(f, v, c), 0);
        let best = cfg[v], bc = here(best) - 1e-9;
        if (bc <= 0) continue;
        for (const c of cand(v)) { const t = here(c); if (t < bc) { bc = t; best = c; } }
        if (best !== cfg[v]) { cfg[v] = best; moved = any = true; }
      }
    }
    return any;
  };
  // (and a REGION at once: the connected vertices holding one arrangement of two groups or three, with the vertices
  //  beside them that hold one of those alone, all in another order of the slots -- where two orders meet along a
  //  seam, no single vertex gains by moving)
  const same = (c, d) => c[0] === d[0] && c[1] === d[1] && c[2] === d[2];
  const regions = () => {
    let any = false;
    const seen = new Int32Array(nv).fill(-1);
    for (let v0 = 0; v0 < nv; v0++) {
      const c0 = cfg[v0];
      if (!c0 || (c0[0] === c0[1] && c0[1] === c0[2]) || seen[v0] >= 0) continue;
      const R = [v0], st = [v0], side = [];
      seen[v0] = v0;
      while (st.length) {
        const v = st.pop();
        for (const u of nbr[v]) {
          const c = cfg[u];
          if (!c || seen[u] === v0) continue;
          if (same(c, c0)) { seen[u] = v0; R.push(u); st.push(u); }
          else if (c[0] === c[1] && c[1] === c[2] && (c[0] === c0[0] || c[0] === c0[1] || c[0] === c0[2])) { seen[u] = v0; side.push(u); }
        }
      }
      const all = [...R, ...side], F = [...new Set(all.flatMap((v) => tris[v]))];
      const total = () => F.reduce((t, f) => t + torn(f, -1, null), 0);
      const keep = all.map((v) => cfg[v]);
      let best = total() - 1e-9, bp = null;
      for (const p of PERMS) {
        all.forEach((v, i) => { const c = keep[i]; cfg[v] = [c[p[0]], c[p[1]], c[p[2]], c[NS + p[0]], c[NS + p[1]], c[NS + p[2]]]; });
        const t = total();
        if (t < best) { best = t; bp = p; }
      }
      if (bp) { any = true; all.forEach((v, i) => { const c = keep[i]; cfg[v] = [c[bp[0]], c[bp[1]], c[bp[2]], c[NS + bp[0]], c[NS + bp[1]], c[NS + bp[2]]]; }); }
      else all.forEach((v, i) => { cfg[v] = keep[i]; });
    }
    return any;
  };
  single();
  for (let round = 0; round < 4 && regions(); round++) single();
  // (5) written: each slot's group in its own frame, at its nearest shape
  const members = Array.from({ length: NG }, () => []);
  for (let i = 0; i < n; i++) members[G.of[i]].push(i);
  const shapeOf = (v, g, x, y, z) => {
    for (let j = 0; j < NS; j++) if (ag[v * NS + j] === g) return as[v * NS + j];
    let bi = members[g][0], bd = Infinity;
    for (const i of members[g]) { const d = patterned[i].d(x, y, z); if (d < bd) { bd = d; bi = i; } }
    return bi;
  };
  for (let v = 0; v < nv; v++) {
    const c = cfg[v];
    if (!c) continue;
    const x = P[3 * v], y = P[3 * v + 1], z = P[3 * v + 2];
    for (let k = 0; k < NS; k++) patternOf(patterned[shapeOf(v, c[k], x, y, z)].src, x, y, z, out, v, k);
    out.kt[NS * v] = Math.min(1, Math.max(0, K[v]));
    out.kt[NS * v + 1] = c[NS + 1];
    out.kt[NS * v + 2] = c[NS + 2];
  }
}
// THIN PARTS drawn as they are (bodyspec.js details): a cone as a smooth lathe of `sides`, a triangle as a plate with
// its two faces, a little ellipsoid as a ball -- each wholly on its own bone
// (a FAIRED fin's view of the body: the field's distance, and its paint, wetness, normal and skin at a point -- the paint
//  as the body's own vertices get it: countershaded and mottled)
function fairContext(F, A, nb, cell, shade, MO) {
  const tmp = new Float64Array(A), w = new Float64Array(nb), si = new Uint16Array(4), sw = new Float32Array(4);
  return { dist: F.dist, cell, attr(x, y, z) {
    tmp.fill(0); F.at(x, y, z, tmp);
    const c = [tmp[0], tmp[1], tmp[2]];
    if (shade) shadeOf(shade, x, y, z, c);
    const k = 1 + MO.amount * (2 * noise3(x * MO.scale, y * MO.scale, z * MO.scale) - 1);
    for (let b = 0; b < nb; b++) w[b] = tmp[NA + b];
    top4(w, nb, si, sw, 0);
    return { c: c.map((v) => v * k), wet: tmp[3], n: gradient(F.dist, x, y, z), si: [...si], sw: [...sw] };
  }, paint(x, y, z, c0) {   // (a colour as the body's vertex there gets it: countershaded and mottled -- a sweep's thin end)
    const c = [c0[0], c0[1], c0[2]];
    if (shade) shadeOf(shade, x, y, z, c);
    const k = 1 + MO.amount * (2 * noise3(x * MO.scale, y * MO.scale, z * MO.scale) - 1);
    return c.map((v) => v * k);
  } };
}
function detailMesh(q, li = 0, bi = () => 0, fairCtx = null) {
  if (q.type === "feathers") return featherMesh(q, li, bi);
  if (q.type === "membrane") return membraneMesh(q, bi);
  if (q.type === "horn") return hornMesh(q, li, bi, fairCtx);   // (a point and an edge, never in the field: sharp.js)
  if (q.type === "fin") return finMesh(q, li, bi, fairCtx);
  if (q.type === "sweep") return sweepMesh(q, li, bi, fairCtx);   // (a sweep's thin end: exact rings, its skin and paint the sweep's)
  const P = [], N = [], T = [];
  if (q.type === "tri") {
    const n = nrm(crs(q.b.map((v, k) => v - q.a[k]), q.c.map((v, k) => v - q.a[k]))), h = Math.max(q.r, 1e-4);
    for (const sgn of [1, -1]) {
      const b0 = P.length / 3;
      for (const C of [q.a, q.b, q.c]) { P.push(...C.map((v, k) => v + n[k] * h * sgn)); N.push(...n.map((v) => v * sgn)); }
      T.push(...(sgn > 0 ? [b0, b0 + 1, b0 + 2] : [b0, b0 + 2, b0 + 1]));
    }
    return { P, N, T };
  }
  if (q.type === "ell" || q.type === "sphere") {
    const c = q.c, R = Array.isArray(q.r) ? q.r : [q.r, q.r, q.r], ax = q.axes ?? [[1, 0, 0], [0, 1, 0], [0, 0, 1]], sg = [8, 5];
    for (let i = 0; i <= sg[1]; i++) for (let j = 0; j <= sg[0]; j++) {
      const th = i / sg[1] * Math.PI, ph = j / sg[0] * 2 * Math.PI, l = [Math.sin(th) * Math.cos(ph), Math.cos(th), Math.sin(th) * Math.sin(ph)];
      P.push(...[0, 1, 2].map((k) => c[k] + ax[0][k] * l[0] * R[0] + ax[1][k] * l[1] * R[1] + ax[2][k] * l[2] * R[2]));
      N.push(...nrm([0, 1, 2].map((k) => ax[0][k] * l[0] / R[0] + ax[1][k] * l[1] / R[1] + ax[2][k] * l[2] / R[2])));
    }
    for (let i = 0; i < sg[1]; i++) for (let j = 0; j < sg[0]; j++) { const a = i * (sg[0] + 1) + j, b = a + 1, d = a + sg[0] + 1, e = d + 1; T.push(a, b, d, b, e, d); }
    return { P, N, T };
  }
  // a cone or a tube: rings along it
  const C = q.type === "tube" ? q.pts.map((t) => [t[0], t[1], t[2], t[3]]) : [[...q.a, q.ra], [...q.b, q.rb]];
  const sides = 6, ring = [];
  for (let i = 0; i < C.length; i++) {
    const t = nrm((C[Math.min(i + 1, C.length - 1)]).slice(0, 3).map((v, k) => v - C[Math.max(i - 1, 0)][k]));
    const ref = Math.abs(t[1]) < .9 ? [0, 1, 0] : [1, 0, 0], u = nrm(crs(t, ref)), w = crs(t, u);
    const slope = (C[C.length - 1][3] - C[0][3]) / (Math.hypot(...C[C.length - 1].slice(0, 3).map((v, k) => v - C[0][k])) || 1);
    ring.push(P.length / 3);
    for (let m = 0; m < sides; m++) {
      const a = m / sides * 2 * Math.PI, d = [0, 1, 2].map((k) => u[k] * Math.cos(a) + w[k] * Math.sin(a));
      P.push(...[0, 1, 2].map((k) => C[i][k] + d[k] * C[i][3])); N.push(...nrm(d.map((v, k) => v - t[k] * slope)));
    }
  }
  for (let i = 0; i + 1 < ring.length; i++) for (let m = 0; m < sides; m++) {
    const a = ring[i] + m, b = ring[i] + (m + 1) % sides, c = ring[i + 1] + m, d = ring[i + 1] + (m + 1) % sides;
    T.push(a, c, b, b, c, d);
  }
  // (caps: a point at each end, so a cut-off cone is closed)
  for (const [i, sgn] of [[0, -1], [C.length - 1, 1]]) {
    const t = nrm(C[C.length - 1].slice(0, 3).map((v, k) => v - C[0][k])), tip = P.length / 3;
    P.push(...[0, 1, 2].map((k) => C[i][k] + t[k] * sgn * C[i][3] * .6)); N.push(...t.map((v) => v * sgn));
    for (let m = 0; m < sides; m++) { const a = ring[i] + m, b = ring[i] + (m + 1) % sides; T.push(...(sgn > 0 ? [a, b, tip] : [b, a, tip])); }
  }
  // (`tip`: its colour fading from `color` to `tip` along its last part, from `tipAt` (of its length) to the end -- an
  //  antler tine's paling point, a horn's dark tip, with no band where a second lathe began)
  if (q.tip) {
    const c0 = rgb(q.color), c1 = rgb(q.tip), at = q.tipAt ?? .5, L = [0];
    for (let i = 1; i < C.length; i++) L.push(L[i - 1] + Math.hypot(...[0, 1, 2].map((k) => C[i][k] - C[i - 1][k])));
    const tot = L[L.length - 1] || 1, mixAt = (i) => { const x = Math.max(0, Math.min(1, (L[i] / tot - at) / (1 - at || 1))); return x * x * (3 - 2 * x); };
    const col = (f) => c0.map((v, k) => v + (c1[k] - v) * f), Cc = [];
    for (let i = 0; i < C.length; i++) { const c = col(mixAt(i)); for (let m = 0; m < sides; m++) Cc.push(...c); }
    Cc.push(...col(mixAt(0)), ...col(mixAt(C.length - 1)));
    return { P, N, T, C: Cc };
  }
  return { P, N, T };
}

// A MEMBRANE (2026-11-06, the pteranodon's wings): a skin stretched between bones -- `pts` (its points where the rest pose
// puts them), `tris` (three indices a face), `bones` (ids) and `skin` (each point's: an index into bones, or [i, j, t]:
// 1 - t of bone i, t of bone j), so a wing's skin spans its arm, its finger and the flank and stretches as they spread
// (a detail plate lies wholly on one bone). Two-sided, `r` apart; `tone` (one a point, optional) scales its colour;
// `nrm` (one a point, optional) gives its normals outright -- a skin folded into pleats at rest has no sound normal of
// its own there, so a wing's are worked out spread and carried back to the rest pose by each point's skinning.
// `under` (optional, default 1) scales the colour of the side its normals point away from: a wing's underside a little
// lighter, as the light comes through the skin from above.
function membraneMesh(q, bi) {
  const n = q.pts.length, P = [], N = [], T = [], C = [], SI = [], SW = [], h = Math.max(q.r ?? .002, 1e-4), c0 = rgb(q.color);
  const nv = new Float64Array(n * 3);
  for (let f = 0; f < q.tris.length; f += 3) {   // (each point's normal: its faces', by their area)
    const [a, b, c] = [q.tris[f], q.tris[f + 1], q.tris[f + 2]], A = q.pts[a];
    const fn = crs(q.pts[b].map((v, k) => v - A[k]), q.pts[c].map((v, k) => v - A[k]));
    for (const v of [a, b, c]) for (let k = 0; k < 3; k++) nv[3 * v + k] += fn[k];
  }
  const bone = q.bones.map((id) => bi(id));
  for (const sgn of [1, -1]) {
    for (let v = 0; v < n; v++) {
      const nn = nrm(q.nrm?.[v] ?? [nv[3 * v], nv[3 * v + 1], nv[3 * v + 2]]), t = (q.tone?.[v] ?? 1) * (sgn < 0 ? q.under ?? 1 : 1), e = q.skin[v];
      P.push(...q.pts[v].map((x, k) => x + nn[k] * h * sgn)); N.push(...nn.map((x) => x * sgn)); C.push(...c0.map((x) => x * t));
      if (Array.isArray(e)) { SI.push(bone[e[0]], bone[e[1]], 0, 0); SW.push(1 - e[2], e[2], 0, 0); } else { SI.push(bone[e], 0, 0, 0); SW.push(1, 0, 0, 0); }
    }
    const o = sgn > 0 ? 0 : n;
    for (let f = 0; f < q.tris.length; f += 3) T.push(...(sgn > 0 ? [q.tris[f], q.tris[f + 1], q.tris[f + 2]] : [q.tris[f], q.tris[f + 2], q.tris[f + 1]]).map((v) => v + o));
  }
  return { P, N, T, C, SI, SW };
}

// FEATHERS (2026-11-04): a row or a fan of real blades -- `n` of them, each rooted on the line its `rows` make (a row:
// { at, dir, len, w, bone, up? }, the feathers spread evenly from the first row to the last, each one's root, direction,
// length, half-width and bones interpolated between the two rows it lies between), each a tapered vane with its two
// sides of its outline (OUTLINE: a flight feather's narrow leading vane and broad trailing one, a round covert or tail
// feather, a peacock's train feather -- a bare shaft that opens into a broad eye), cambered across (`camber`, of its
// width) and curved along (`curve`, of its length) toward `up`, lifted off its row by `lift` (a layer of coverts over
// the flight feathers) and `stagger` (alternate feathers, so overlapping vanes never fight), its length varied by
// `vary`. Two-sided. Its colour runs from `color` at the root to `tip`; the vane's fine work is per pixel (coatpat.js
// feather: the barbs, the rachis, `bars`, the `ocellus`) from the feather's own coordinates. Its skin: the bones of the
// rows it lies between, by how far it is from each -- a wing folds at the wrist and a tail spreads, feather by feather.
const OUTLINE = {
  flight: (t) => { const b = Math.min(1, t / .14) ** .6 * Math.max(0, 1 - t ** 3.2) ** .55; return [b * .42, b]; },
  round: (t) => { const b = Math.sin(Math.PI * Math.min(1, t) ** .8) ** .55 * Math.min(1, t / .1) ** .5; return [b * .9, b]; },
  train: (t) => { const e = 1 / (1 + Math.exp(-(t - .82) / .03)), tipR = t > .93 ? Math.sqrt(Math.max(0, 1 - ((t - .93) / .07) ** 2)) : 1;
                  const b = (.36 + .64 * e) * tipR * Math.min(1, t / .04); return [b, b]; },
};
function featherMesh(q, li, bi) {
  const P = [], N = [], T = [], C = [], SI = [], SW = [], PI = [], PP = [], PQ = [];
  const rows = q.rows, R = rows.length, n = Math.max(1, q.n ?? 8), r = rng(q.seed ?? 7), out = OUTLINE[q.outline] ?? OUTLINE.round;
  const nt = li ? 4 : 10, cs = li ? [-1, 0, 1] : [-1, -.5, 0, .5, 1];
  const c0 = rgb(q.color), c1 = rgb(q.tip ?? q.color);
  const bars = q.bars ? [q.bars.n ?? 5, q.bars.dark ?? .4] : [0, 0], oc = q.ocellus ? [q.ocellus.at ?? .88, q.ocellus.r ?? .85] : [0, 0];
  for (let j = 0; j < n; j++) {
    const u = n === 1 ? 0 : j / (n - 1), x = u * (R - 1), i0 = Math.min(R - 2, Math.floor(x)), t = R === 1 ? 0 : x - Math.max(0, i0), A = rows[Math.max(0, i0)], B = rows[Math.min(R - 1, Math.max(0, i0) + 1)];
    const L = (k) => (A[k] + (B[k] - A[k]) * t);
    const root = [0, 1, 2].map((k) => A.at[k] + (B.at[k] - A.at[k]) * t), jit = (q.jitter ?? 0) * (r() - .5);
    let d = nrm([0, 1, 2].map((k) => A.dir[k] + (B.dir[k] - A.dir[k]) * t));
    const len = L("len") * (1 - (q.vary ?? 0) * r()), w = L("w") * (1 + (r() - .5) * .12);
    // its up: the row's, or the fan's, or square to the root line and the feather
    const upR = A.up && B.up ? [0, 1, 2].map((k) => A.up[k] + (B.up[k] - A.up[k]) * t) : q.up ?? (() => { const tg = R > 1 ? B.at.map((v, k) => v - A.at[k]) : [0, 0, 1], c = crs(tg, d); return c[1] < 0 ? c.map((v) => -v) : c; })();
    let up = nrm(upR.map((v, k) => v - d[k] * dot3(upR, d)));
    let side = nrm(crs(d, up));
    if (jit) { const ca = Math.cos(jit), sa = Math.sin(jit); d = nrm(d.map((v, k) => v * ca + side[k] * sa)); side = nrm(crs(d, up)); }
    const lift = (q.lift ?? 0) + (j % 2 ? q.stagger ?? 0 : 0) + j * (q.stack ?? 0);
    // (its skin: the two rows' bones, by where it lies between them)
    const bA = bi(A.bone ?? q.bone), bB = bi(B.bone ?? q.bone), wB = bA === bB ? 0 : t;
    const tone = 1 + (r() - .5) * .14, camber = (q.camber ?? .1) * w, curve = (q.curve ?? 0) * len, th = Math.max(4e-4, w * .03);
    const grid = [];
    // (rows closer toward the tip, where the outline turns)
    const sOf = (a) => 1 - (1 - a / nt) ** 1.8;
    for (let a = 0; a <= nt; a++) {
      const s = sOf(a), wd = out(s), rowP = [];
      for (const c of cs) {
        const half = c < 0 ? wd[0] : wd[1], off = w * half * c, bow = camber * Math.max(wd[0], wd[1]) * (1 - c * c);
        rowP.push([0, 1, 2].map((k) => root[k] + d[k] * len * s + side[k] * off + up[k] * (lift + bow + curve * s * s)));
      }
      grid.push(rowP);
    }
    for (const face of [1, -1]) {
      const b0 = P.length / 3;
      for (let a = 0; a <= nt; a++) for (let ci = 0; ci < cs.length; ci++) {
        const g = grid[a][ci], gt = grid[Math.min(nt, a + 1)][ci].map((v, k) => v - grid[Math.max(0, a - 1)][ci][k]);
        const gc = grid[a][Math.min(cs.length - 1, ci + 1)].map((v, k) => v - grid[a][Math.max(0, ci - 1)][k]);
        let nn = crs(gc, gt);
        if (dot3(nn, up) < 0) nn = nn.map((v) => -v);
        if (Math.hypot(...nn) < 1e-12) nn = up;
        nn = nrm(nn).map((v) => v * face);
        P.push(...g.map((v, k) => v - up[k] * (face < 0 ? th : 0))); N.push(...nn);
        const s = sOf(a), m = s ** 1.4;
        C.push(...[0, 1, 2].map((k) => (c0[k] + (c1[k] - c0[k]) * m) * tone));
        SI.push(bA, bB, 0, 0); SW.push(1 - wB, wB, 0, 0);
        const wd = out(s), half = cs[ci] < 0 ? wd[0] : wd[1];
        PI.push(23, 0); PP.push(len * s, w * half * cs[ci], len, w); PQ.push(bars[0], bars[1], oc[0], oc[1]);
      }
      const nc = cs.length;
      for (let a = 0; a < nt; a++) for (let ci = 0; ci + 1 < nc; ci++) {
        const v0 = b0 + a * nc + ci, v1 = v0 + 1, v2 = v0 + nc, v3 = v2 + 1;
        // (wound so its face looks along +up for the front, -up for the back)
        if (face > 0) T.push(v0, v2, v1, v1, v2, v3); else T.push(v0, v1, v2, v1, v3, v2);
      }
    }
  }
  // (each triangle wound so that it faces its normal: checked once, flipped if the frame came out the other hand)
  for (let f = 0; f < T.length; f += 3) {
    const [a, b, c] = [T[f], T[f + 1], T[f + 2]], e1 = [0, 1, 2].map((k) => P[3 * b + k] - P[3 * a + k]), e2 = [0, 1, 2].map((k) => P[3 * c + k] - P[3 * a + k]);
    const fn = crs(e1, e2), nA = [N[3 * a], N[3 * a + 1], N[3 * a + 2]];
    if (dot3(fn, nA) < 0) { T[f + 1] = c; T[f + 2] = b; }
  }
  return { P, N, T, C, SI, SW, pat: { id: PI, p: PP, q: PQ } };
}

// the eyeball: rings round its own front (the surface's normal where it sits), so the pupil and the iris are rings,
// sharp at any size: the pupil a disc (a slit: squeezed across, a bar: squeezed up), the iris round it, the rest darker
function eyeMesh(e, li) {
  const P = [], N = [], C = [], T = [], n = e.n, ref = Math.abs(n[1]) < .9 ? [0, 1, 0] : [1, 0, 0], u = nrm(crs(ref, n)), w = crs(n, u);
  const iris = e.iris != null ? rgb(e.iris) : null, dark = rgb(e.color), pupil = [.012, .01, .009];
  // (latitudes from the front: the pupil's edge, the iris's, then on round the back)
  const lat = iris ? [0, .22, .3, .62, .72, 1.1, 1.6, 2.2, 3.14159] : [0, .5, 1, 1.6, 2.2, 3.14159];
  const seg = li ? 10 : 16, sq = e.pupil === "slit" ? [.35, 1] : e.pupil === "bar" ? [1, .45] : [1, 1];
  lat.forEach((th, i) => {
    for (let j = 0; j <= seg; j++) {
      const ph = j / seg * 2 * Math.PI, k = Math.min(1, (th - .22) / .05);
      // (the pupil's rim squeezed toward its slit or bar; past the iris round again)
      const s0 = th <= .3 ? 1 : 0, sx = 1 + (sq[0] - 1) * s0, sy = 1 + (sq[1] - 1) * s0;
      const st = Math.sin(th), d = [0, 1, 2].map((q) => n[q] * Math.cos(th) + (u[q] * Math.cos(ph) * sx + w[q] * Math.sin(ph) * sy) * st);
      const dn = nrm(d);
      P.push(...e.c.map((v, q) => v + dn[q] * e.r)); N.push(...dn);
      C.push(...(!iris ? dark : th < .25 ? pupil : th < .66 ? iris.map((v, q) => v * (.75 + .25 * k)) : dark));
    }
  });
  for (let i = 0; i + 1 < lat.length; i++) for (let j = 0; j < seg; j++) {
    const a = i * (seg + 1) + j, b = a + 1, d = a + seg + 1, f = d + 1;
    T.push(a, d, b, b, d, f);
  }
  return { P, N, C, T };
}

function assemble(m, A, nb, eyes, coat, li, details, F, bi, PO, shade, MO = MOTTLE, fairCtx = null) {
  const nv = m.pos.length / 3;
  const em = eyes.map((e) => eyeMesh(e, li)), dm = details.map((q) => detailMesh(q, li, bi, q.fair || q.type === "sweep" ? fairCtx : null));
  const ev = em.reduce((s, e) => s + e.P.length / 3, 0), et = em.reduce((s, e) => s + e.T.length / 3, 0);
  const dv = dm.reduce((s, e) => s + e.P.length / 3, 0), dt = dm.reduce((s, e) => s + e.T.length / 3, 0);
  const qv = coat ? coat.pos.length / 3 : 0;
  const V = nv + ev + dv + qv, T = m.tri.length / 3 + et + dt + (coat ? coat.tri.length / 3 : 0);
  const pos = new Float32Array(V * 3), nor = new Float32Array(V * 3), col = new Float32Array(V * 3), wet = new Float32Array(V), hair = new Float32Array(V);
  const uv = new Float32Array(V * 2), si = new Uint16Array(V * 4), sw = new Float32Array(V * 4), index = new Uint32Array(T * 3);
  const pat = { id: new Float32Array(V * 3), kt: new Float32Array(V * 3), p: new Float32Array(V * 4), q: new Float32Array(V * 4), r: new Float32Array(V * 4) };   // (always there: one material draws them all)
  const patterned = F ? patternGroups(F.prims.filter((q) => !q.sub && !q.paint && q.src.pat)) : null;
  // (a DETAIL with a coat pattern and no frame of its own -- a fin sheet, a horn -- takes the frame of the nearest field
  //  shape painted with the same pattern: the spots on a whale shark's tail fin as big as those on its tail stock, and
  //  continuous across the seam; a membrane's own `r` is its thickness, not a girth)
  if (patterned) for (const q of details) {
    if (!q.pat || q._frame || q.patFrame || q.animalFrame || q.type === "feathers") continue;
    const at = q.type === "horn" || q.type === "tube" || q.type === "sweep" ? q.pts[0] : q.type === "fin" ? q.root[0] : q.type === "membrane" ? q.pts[0] : q.c ?? q.a;
    let best = null, bd = Infinity;
    if (at) for (const r of patterned) if (r.src.pat === q.pat) { const d = r.d(at[0], at[1], at[2]); if (d < bd) { bd = d; best = r.src; } }
    if (best) q._frame = best._frame ?? patFrame(best);
  }
  const w = new Float64Array(nb), sc = [0, 0, 0];
  // the body
  for (let v = 0; v < nv; v++) {
    const a = m.attr.subarray(v * A, v * A + A), x = m.pos[3 * v], y = m.pos[3 * v + 1], z = m.pos[3 * v + 2];
    const k = 1 + MO.amount * (2 * noise3(x * MO.scale, y * MO.scale, z * MO.scale) - 1);
    pos.set(m.pos.subarray(3 * v, 3 * v + 3), 3 * v); nor.set(m.nor.subarray(3 * v, 3 * v + 3), 3 * v);
    sc[0] = a[0]; sc[1] = a[1]; sc[2] = a[2];
    if (shade) shadeOf(shade, x, y, z, sc);
    col[3 * v] = sc[0] * k; col[3 * v + 1] = sc[1] * k; col[3 * v + 2] = sc[2] * k; wet[v] = a[3]; hair[v] = a[4];
    for (let b = 0; b < nb; b++) w[b] = a[NA + b];
    top4(w, nb, si, sw, 4 * v);
  }
  // (the patterns: the three groups each vertex needs, chosen over the whole mesh so its triangles agree -- patternsMesh)
  if (patterned) patternsMesh(patterned, m.pos, m.tri, nv, Float64Array.from({ length: nv }, (_, v) => m.attr[v * A + PO]), pat);
  index.set(m.tri, 0);
  let vo = nv, to = m.tri.length;
  const put = (G, colour, bone, src) => {
    const base = vo, c = colour != null ? rgb(colour) : null;
    for (let i = 0; i < G.P.length / 3; i++) {
      pos.set(G.P.slice(3 * i, 3 * i + 3), 3 * vo); nor.set(G.N.slice(3 * i, 3 * i + 3), 3 * vo);
      col.set(G.C ? G.C.slice(3 * i, 3 * i + 3) : c, 3 * vo);
      if (G.SI) { si.set(G.SI.slice(4 * i, 4 * i + 4), 4 * vo); sw.set(G.SW.slice(4 * i, 4 * i + 4), 4 * vo); } else { si[4 * vo] = bone; sw[4 * vo] = 1; }
      if (G.pat) {   // (its own pattern coordinates: a feather's)
        pat.id.set(G.pat.id.slice(2 * i, 2 * i + 2), 3 * vo); pat.p.set(G.pat.p.slice(4 * i, 4 * i + 4), 4 * vo); pat.q.set(G.pat.q.slice(4 * i, 4 * i + 4), 4 * vo);
        pat.kt[3 * vo] = 1;
      } else if (F && src?.pat && (!G.PM || G.PM[i])) { patternOf(src, G.P[3 * i], G.P[3 * i + 1], G.P[3 * i + 2], pat, vo); pat.kt[3 * vo] = 1; }   // (a fin painted on one face only: PM)
      vo++;
    }
    for (let i = 0; i < G.T.length; i++) index[to + i] = base + G.T[i];
    to += G.T.length;
  };
  em.forEach((G, i) => { const b0 = vo; put(G, null, eyes[i].bone, null); wet.fill(1, b0, vo); });
  dm.forEach((G, i) => { const b0 = vo, q = details[i]; put(G, q.color, bi(q.bone), q); if (G.W) wet.set(G.W, b0); else if (q.wet && (q.type === "horn" || q.type === "fin")) wet.fill(q.wet, b0, vo);
    if (q.type === "sweep" && q.hair) hair.fill(q.hair, b0, vo); });   // (a sweep's thin end haired as its field part is: no change of tone where it goes over)
  // the coat
  if (coat) {
    pos.set(coat.pos, 3 * vo); nor.set(coat.nor, 3 * vo); col.set(coat.col, 3 * vo); hair.fill(1, vo, vo + qv); uv.set(coat.uv, 2 * vo);
    si.set(coat.si, 4 * vo); sw.set(coat.sw, 4 * vo);
    for (let q = 0; q < coat.tri.length; q++) index[to + q] = vo + coat.tri[q];
    vo += qv; to += coat.tri.length;
  }
  return { pos, nor, col, wet, hair, uv, skinIndex: si, skinWeight: sw, index, patId: pat.id, patKT: pat.kt, patP: pat.p, patQ: pat.q, patR: pat.r };
}

// THE COAT: quills sown on the fine mesh (blue noise), where the coat is and its rule holds
function sowCoat(F, nets, A, nb, T, seed) {
  const r = rng(seed), P = nets.pos, X = nets.tri, nf = X.length / 3, tmp = new Float64Array(A);
  // the coat's triangles (any corner in it), by area
  const cv = new Float32Array(P.length / 3);
  for (let v = 0; v < cv.length; v++) { tmp.fill(0); F.at(P[3 * v], P[3 * v + 1], P[3 * v + 2], tmp); cv[v] = tmp[5]; }
  const tri = [], cdf = [];
  let area = 0;
  for (let f = 0; f < nf; f++) {
    const a = X[3 * f], b = X[3 * f + 1], c = X[3 * f + 2];
    if (Math.max(cv[a], cv[b], cv[c]) < T.hold * .6) continue;
    const u = [0, 1, 2].map((k) => P[3 * b + k] - P[3 * a + k]), w = [0, 1, 2].map((k) => P[3 * c + k] - P[3 * a + k]);
    area += Math.hypot(...crs(u, w)) / 2; tri.push(f); cdf.push(area);
  }
  const cB = rgb(T.base), cT = rgb(T.tip), cD0 = rgb(T.darkTip ?? T.base), cD = cD0.map((v, k) => v + (cT[k] - v) * .25);
  const pos = [], nor = [], col = [], uv = [], si = [], sw = [], idx = [];
  // BANDS (a porcupine's quills, 2026-11-06): [[f, colour], ...] -- from f of its length on (root 0, tip 1) that colour,
  // the base's below the first; each change a pair of rings at the one place, so the bands meet sharp, not blurred
  const bandF = T.bands ? [0, ...T.bands.map((b) => b[0])] : null, bandC = T.bands ? [cB, ...T.bands.map((b) => rgb(b[1]))] : null;
  const banded = (ring0, root, d, L, rr, kk, u0, wI, wW) => {
    const ns = ring0.length, at = (f) => ring0.map((Q) => Q.map((x, k) => root[k] + (x - root[k]) * (1 - f) + d[k] * L * f));
    const put = (Q, f, c, m) => { pos.push(...Q); const ctr = root.map((x, k) => x + d[k] * L * f);
      nor.push(...nrm(Q.map((x, k) => x - ctr[k] + d[k] * rr * .3))); col.push(c[0] * kk, c[1] * kk, c[2] * kk); uv.push(u0 + m * .05, f * L); si.push(...wI); sw.push(...wW); };
    const face = (a, b, c, ctr) => {   // (outward from the quill's axis)
      const A = pos.slice(3 * a, 3 * a + 3), B = pos.slice(3 * b, 3 * b + 3), C = pos.slice(3 * c, 3 * c + 3);
      const N = crs(B.map((x, k) => x - A[k]), C.map((x, k) => x - A[k])), mid = A.map((x, k) => (x + B[k]) / 2 - ctr[k]);
      idx.push(...(N[0] * mid[0] + N[1] * mid[1] + N[2] * mid[2] >= 0 ? [a, b, c] : [b, a, c]));
    };
    const last = bandF.length - 1;
    for (let i = 0; i <= last; i++) {
      const f0 = bandF[i], c = bandC[i], lo = at(f0), b0 = pos.length / 3, ctr = root.map((x, k) => x + d[k] * L * f0);
      lo.forEach((Q, m) => put(Q, f0, c, m));
      if (i < last) {
        const f1 = bandF[i + 1], hi = at(f1), b1 = pos.length / 3;
        hi.forEach((Q, m) => put(Q, f1, c, m));
        for (let m = 0; m < ns; m++) { const m1 = (m + 1) % ns; face(b0 + m, b0 + m1, b1 + m, ctr); face(b0 + m1, b1 + m1, b1 + m, ctr); }
      } else {
        const tip = root.map((x, k) => x + d[k] * L), bt = pos.length / 3;
        put(tip, 1, c, 0);
        for (let m = 0; m < ns; m++) face(b0 + m, b0 + (m + 1) % ns, bt, ctr);
      }
    }
  };
  const md = T.gap * .85, cell = md, grid = new Map(), key = (i, j, k) => `${i},${j},${k}`;
  const near = (p) => {
    const i = Math.floor(p[0] / cell), j = Math.floor(p[1] / cell), k = Math.floor(p[2] / cell);
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++)
      for (const q of grid.get(key(i + a, j + b, k + c)) ?? []) if ((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 + (q[2] - p[2]) ** 2 < md * md) return true;
    return false;
  };
  const darts = Math.ceil(area / (T.gap * T.gap) * 6), wI = new Uint16Array(4), wW = new Float32Array(4), wv = new Float64Array(nb);
  let n = 0;
  for (let t = 0; t < darts && tri.length; t++) {
    // a point on a triangle by area: binary search the running sum
    const s = r() * area;
    let lo = 0, hi = cdf.length - 1;
    while (lo < hi) { const m = (lo + hi) >> 1; if (cdf[m] < s) lo = m + 1; else hi = m; }
    const f = tri[lo], [a, b, c] = [X[3 * f], X[3 * f + 1], X[3 * f + 2]];
    let u = r(), v = r(); if (u + v > 1) { u = 1 - u; v = 1 - v; }
    const p0 = [0, 1, 2].map((k) => P[3 * a + k] + (P[3 * b + k] - P[3 * a + k]) * u + (P[3 * c + k] - P[3 * a + k]) * v);
    const q = onSurface(F.dist, p0, 2);
    if (near(q)) continue;
    tmp.fill(0); F.at(q[0], q[1], q[2], tmp);
    const cover = tmp[5];
    if (cover < T.hold) continue;
    const nn = gradient(F.dist, q[0], q[1], q[2]);
    const sk = T.skirt + Math.max(0, nn[0] - T.face) / (1 - T.face) * T.rise - Math.max(0, -nn[0] - .2) / .8 * T.drop;
    if (nn[1] < sk) continue;
    if (T.sparse && r() < T.sparse * (1 - Math.max(0, nn[1]))) continue;   // (sparse: thinned toward the flanks -- the most on a vertical side)
    const i0 = Math.floor(q[0] / cell), j0 = Math.floor(q[1] / cell), k0 = Math.floor(q[2] / cell), kk0 = key(i0, j0, k0);
    if (!grid.has(kk0)) grid.set(kk0, []);
    grid.get(kk0).push(q);
    n++;
    // its skin: its root's
    for (let bb = 0; bb < nb; bb++) wv[bb] = tmp[NA + bb];
    top4(wv, nb, wI, wW, 0);
    const edge = Math.min(1, (nn[1] - sk) / .35, (cover - T.hold) / Math.max(.05, 1 - T.hold) * 1.6);
    let bk = [-1 + nn[0] * nn[0], nn[0] * nn[1], nn[0] * nn[2]];
    bk = Math.hypot(...bk) > 1e-3 ? nrm(bk) : [0, -1, 0];
    const jit = nrm([r() - .5, r() - .5, r() - .5]);
    const ln = T.fan ? Math.max(.05, T.lean - T.fan * Math.max(0, cover - (T.fanAt ?? 1))) : T.lean;   // (fan: raised where the coat is over fanAt -- a rump's fan)
    const d = nrm([0, 1, 2].map((k) => nn[k] * (1 - ln) + bk[k] * ln + jit[k] * T.vary));
    const brow = nn[0] > T.face ? 1 - .45 * (nn[0] - T.face) / (1 - T.face) : 1;
    const L = T.len * (.5 + .5 * edge) * brow * Math.max(1, cover) * (1 + (r() - .5) * .35), rr = T.r * (1 + (r() - .5) * .3);
    const t1 = nrm(Math.abs(d[1]) < .9 ? crs(d, [0, 1, 0]) : crs(d, [1, 0, 0])), t2 = crs(d, t1);
    const root = q.map((x, k) => x - nn[k] * rr * 1.2), tipP = root.map((x, k) => x + d[k] * L);
    const a0 = r() * Math.PI, ns = T.sides;
    const ring = Array.from({ length: ns }, (_, m) => { const an = a0 + m * 2 * Math.PI / ns, ca = Math.cos(an) * rr, sa = Math.sin(an) * rr;
                                                        return root.map((x, k) => x + t1[k] * ca + t2[k] * sa); });
    // four vertices a quill -- its three root corners and its tip -- smooth-shaded: the corners' normals out from its
    // axis, the tip's along it bent toward the skin's (a round spine catching the light down its length)
    const ct = r() < T.dark ? cD : cT, kk = 1 + (r() - .5) * .2, u0 = r() * 7, base = pos.length / 3;
    if (bandC) { banded(ring, root, d, L, rr, kk, u0, wI, wW); continue; }
    ring.forEach((Q, m) => {
      pos.push(...Q); nor.push(...nrm(Q.map((x, k) => x - root[k] + d[k] * rr * .3)));
      col.push(cB[0] * kk, cB[1] * kk, cB[2] * kk); uv.push(u0 + m * .05, 0); si.push(...wI); sw.push(...wW);
    });
    pos.push(...tipP); nor.push(...nrm(d.map((x, k) => x * .4 + nn[k]))); col.push(ct[0] * kk, ct[1] * kk, ct[2] * kk); uv.push(u0, L); si.push(...wI); sw.push(...wW);
    for (let m = 0; m < ns; m++) {
      const P1 = ring[m], P2 = ring[(m + 1) % ns], N = crs(P2.map((x, k) => x - P1[k]), tipP.map((x, k) => x - P1[k]));
      const mid = P1.map((x, k) => (x + P2[k]) / 2 - root[k]), out = N[0] * mid[0] + N[1] * mid[1] + N[2] * mid[2] >= 0;
      idx.push(...(out ? [base + m, base + (m + 1) % ns, base + ns] : [base + (m + 1) % ns, base + m, base + ns]));
    }
  }
  return { n, pos: Float32Array.from(pos), nor: Float32Array.from(nor), col: Float32Array.from(col), uv: Float32Array.from(uv),
           si: Uint16Array.from(si), sw: Float32Array.from(sw), tri: Uint32Array.from(idx) };
}
