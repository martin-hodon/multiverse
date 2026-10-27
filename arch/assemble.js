// DEFINITIONS: the JSON layer. What a building IS, in terms of what it is made of, all the way down to the
// arch profiles -- and nothing about triangles, which is build.js's business.
//
// Three rules keep the definitions readable as they grow:
//   1. Every number may be an EXPRESSION over the params: "rOuter - wallT", "storeyH * 0.62". No eval: a
//      twenty-line parser that knows names, numbers, + - * / and brackets, and nothing else.
//   2. A part may be USED by another part. The lowest level is an opening's head (a profile), then a wall
//      face, then a bay, then a ring or a row of bays, then a storey. Each level only names the one below.
//   3. Repetition is described, not written out: a wall says its openings as a PATTERN -- "2-3-2" is three
//      blocks of two, three and two openings, with the block gap wider than the opening gap -- and a ring
//      says how many bays, not where each one goes.
import { wallFace, stepsFace, tunnelFace, extrude, straight, straightAt, radial, chordal, sweep, corridor, flank, along, mesh, domeShell, domeRibs, groinRibs, pendentives, frame, groinVault, roofMesh, roofLevels, overhang, chamferLevels, curvedRoof, flightFace, slabFace, helix, helixAlong, staircase, drum, box, cofferedSurface, planPoints, prismMesh, wellPoints, stackMesh, enclosureMesh, flyerMesh, tieredWall, insetPoints, innerAlong, glassPanes } from "./build.js";
import { archCurve } from "./profiles.js";
import { basilica, basilicaLevels } from "./gothic.js";
import { wardDefs } from "./castle.js";   // THE FORTIFIED WARD: curtain, flanking towers, gate, wall walk, loops, newel stairs   // THE VAULTED BASILICA as its structure: piers, arches, rib vaults, buttresses, roofs
import { coursesOf, coursesMesh, faceGaps } from "./courses.js";   // COURSES: plinth, string courses, cornice run along a wall's face
import { orderSize, pilasterSpots, pilasterMesh } from "./order.js";   // THE APPLIED ORDER: pilasters and entablature, sized from the storey
import { index as solidIndex, insideOf, cellOf, heightOver } from "./solid.js";
import { fitFurniture } from "./room.js";   // the furniture given room: moved off chimneys, columns and doorways, or left out
import { domeRows, earClip, lathe } from "./build.js";
import { gableFriezeMesh } from "./lombard.js";
import { helmMesh } from "./helm.js";
import { shikharaMesh, shikharaHeight, samvaranaMesh, samvaranaHeight } from "./shikhara.js";
import { evalNum, evalValue } from "../expr.js";
import { buildItem } from "../items.js";   // FURNITURE: the rooms' chairs, tables, beds and chests are items (assets/items/furniture)
import FURNISHING from "../assets/architecture/furnishing.json" with { type: "json" };   // what a `zone` is filled with

// ---- expressions: one parser for every definition in the project (expr.js) ---------------------------------
const num_ = evalNum, value_ = evalValue;

// THE DETAIL LEVEL, in powers of two: `per90` points per 90 degrees of arc, for everything round in the
// building -- arch heads, drums, and the domes to come. 2 is the coarse setting (four segments over a Roman
// arch), 4 comfortable, 8 and 16 for a close look. It is snapped to a power of two so the settings are a
// ladder rather than a dial, and so halving it exactly halves the points on every curve.
export const detailOf = (params) => {
  const v = Math.max(1, Math.min(32, num_(params.detail ?? 2, params)));
  return 2 ** Math.round(Math.log2(v));
};
// ...AND BY SIZE: a great dome 30m across needs far more points on its curve than a lantern 2m across to look as
// smooth, so a round thing's detail follows its radius -- the building's detail at about 4m, twice it at 8m, four
// times at 16m (to the nearest power of two: from about 11m), up to `maxDetail` (16 unless the building says), and
// half of it under 2m (lanterns, finials, the shafts of columns).
export const detailFor = (params, radius) => {
  const d = detailOf(params), cap = Math.max(d, num_(params.maxDetail ?? 16, params));
  const v = radius < 2 ? d / 2 : d * Math.max(1, radius / 4);
  return Math.max(1, Math.min(cap, 2 ** Math.round(Math.log2(v))));
};

// THE ORDERS, as proportions of the shaft's radius: how tall the base (`base`) and how far it spreads (`baseR`),
// the capital's height (`cap`) and its abacus's half-width (`capR`), the abacus's share of the capital
// (`abacus`, the rest being the echinus or the bell), how far that flare reaches toward the abacus (`flare`),
// and the shaft's taper. Doric has no base; Ionic carries volutes; Corinthian a tall bell. (Data, not cases:
// a new order is a new line.)
export const ORDERS = {
  doric:      { base: 0,   baseR: 1,    cap: 1.0, capR: 1.2,  abacus: .45, flare: .95, taper: .78 },
  tuscan:     { base: .5,  baseR: 1.3,  cap: .9,  capR: 1.35, abacus: .4,  flare: .8,  taper: .85 },
  ionic:      { base: .55, baseR: 1.35, cap: .75, capR: 1.35, abacus: .3,  flare: .75, taper: .86, volutes: true },
  corinthian: { base: .55, baseR: 1.35, cap: 2.3, capR: 1.45, abacus: .18, flare: .9,  taper: .86 },
  // THE EGYPTIAN COLUMNS, in the same radius: a flat round disc for a base, the shaft barely narrowing, and over it
  //   HATHORIC (Dendera's): the goddess's four-faced block, the sistrum's little shrine on her head with its own
  //   cornice, and an abacus no wider than the shaft -- `hathor` the shares of the capital's height each takes;
  //   CAMPANIFORM (the open papyrus, the Ptolemaic composite): a bell flaring out to `capR`, and on its broad top an
  //   abacus only as wide as the shaft, so from below the architrave seems to float over the flowers
  hathoric:    { base: .4,  baseR: 1.22, cap: 3.8, capR: 1.18, abacus: .1,  flare: 1,   taper: .94, hathor: { block: .52, naos: .3, naosR: .86, lip: .08 } },
  campaniform: { base: .4,  baseR: 1.22, cap: 2.4, capR: 1.75, abacus: .14, flare: 1,   taper: .9,  bell: true },
};

// An arch head's own numbers are expressions too -- "seg", "storeyH * 0.2" -- so they are evaluated here
// rather than handed to the profile as text. (The profile layer is mathematics and takes numbers only.) The
// building's detail level rides along, unless the head names a segment count of its own.
// A WORD that may name a PARAMETER holding one ("profile": "arch", with "arch": "pointed"; "form": "roofForm"),
// and a parameter may point at another ("naveArch": "arch", "arch": "pointed") -- so a part follows the
// building's own choice unless it is given one of its own
const wordOf = (w, params) => { for (let i = 0; i < 4 && typeof w === "string" && typeof params[w] === "string"; i++) w = params[w]; return w; };
const headOf = (h, params) => {
  const out = { ...(h ?? {}) };
  for (const k of ["seg", "rise", "spread", "over", "bulge", "neck", "lobe", "bow", "waist", "lift", "lo", "hi", "cap", "slope", "steps"]) if (k in out) out[k] = num_(out[k], params);
  // (the profile may name a parameter: every opening in a building follows one decision)
  out.profile = wordOf(out.profile, params);
  out.per90 = detailOf(params);
  return out;
};
// A DOME'S MERIDIAN, struck with `head` over `radius` at the detail its size asks for -- the one curve the dome, the
// ribs laid on it and a stair winding up under it are all set out from
const domeCurve = (radius, head, params) => archCurve(radius, headOf(head, { ...params, detail: detailFor(params, radius) }));

// ---- openings ------------------------------------------------------------------------------------------------
// "2-3-2": three blocks of 2, 3 and 2 openings. Within a block the openings are `gap` apart; between blocks the
// pier is `pier` wide; the ends carry half a pier each unless `end` says otherwise. The wall's width follows
// from that, which is the point: you say the rhythm, the engine says how long the wall is.
export function patternOpenings(p, params) {
  // "2-3-2" is three blocks of two, three and two openings -- and each count may be an EXPRESSION, so a
  // building says "bays" and one parameter changes how many arches it has
  const blocks = String(p.pattern).split("-").map((n) => Math.max(1, Math.round(num_(n, params))));
  const w = num_(p.width, params), gap = num_(p.gap ?? 0, params), pier = num_(p.pier ?? p.gap ?? 0, params);
  const end = num_(p.end ?? pier / 2, params);
  const head = headOf(p.head, params), sill = num_(p.sill ?? 0, params);
  // `middle`: the opening in the middle of an odd row is another -- a gate among the windows, a portal among the
  // arches -- { width, sill, springing, head, glass }; the row stays centred on it
  const total = blocks.reduce((a, b) => a + b, 0), mid = p.middle && total % 2 === 1 ? (total - 1) / 2 : -1;
  const mw = mid >= 0 ? num_(p.middle.width ?? p.width, params) : 0;
  const out = [];
  let x = end, i = 0;
  blocks.forEach((n, b) => {
    for (let k = 0; k < n; k++, i++) {
      const m = i === mid, ow = m ? mw : w, q = m ? { ...p, ...p.middle } : p;
      out.push({ at: x + ow / 2, width: ow, sill: m ? num_(q.sill ?? 0, params) : sill, springing: num_(q.springing ?? q.sill ?? 0, params),
                 head: m && p.middle.head ? headOf(p.middle.head, params) : head,
                 ...(q.foot ? { foot: headOf(q.foot, params) } : {}), ...glassOf(q, params), ...traceryOf(q, params), ...wimpergOf(q, params), ...surroundOf(q, params) });
      x += ow + (k + 1 < n ? gap : 0);
    }
    if (b + 1 < blocks.length) x += pier;
  });
  return { openings: out, width: x + end };
}

// ---- parts ---------------------------------------------------------------------------------------------------
// Each part builds ONE geometry and says how many times, and where, it is drawn. A ring's bay is built once in
// its own wedge and the ring is made by rotating it: the rotation is exact, so the bays meet exactly.

// WHICH BAYS A PART STANDS IN. A ring of 60 is not 60 of the same thing: every fifth bay is a vomitorium, two
// opposite ones are the main entrances that run straight through to the arena, and the rest are plain. So a
// part says which bays are its own -- `every`/`offset` with `only: "every"` to take them rather than leave
// them, `at` for named bays, `skip` for the exceptions carved out of a rule.
// An extra rotation in BAYS, added to the bay index. A switchback's landing belongs to no single bay: it
// straddles the two the flights climb in, so it is placed at `turn: 0.5`.
const turnOf = (def, n, P) => P(def.turn, 0) * 2 * Math.PI / n;

function baysFor(def, n, P) {
  const every = Math.max(1, Math.round(P(def.every, 1))), offset = Math.round(P(def.offset, 0));
  // `range: [first, last]`: the bays from one to the other, going round (expressions, so a component can say
  // "the bays of an arc" in terms of its own params)
  const range = def.range ? (() => { const a = Math.round(P(def.range[0])), b = Math.round(P(def.range[1])), out = [];
    for (let k = a; k <= b; k++) out.push(((k % n) + n) % n); return out; })() : null;
  const at = def.at ? def.at.map((v) => ((Math.round(P(v)) % n) + n) % n) : range;
  const skip = new Set((def.skip ?? []).map((v) => ((Math.round(P(v)) % n) + n) % n));
  const out = [];
  for (let k = 0; k < n; k++) {
    if (at) { if (!at.includes(k)) continue; }
    else if (every > 1) {
      const isEvery = ((k - offset) % every + every) % every === 0;
      if (def.only === "every" ? !isEvery : isEvery) continue;
    }
    if (!skip.has(k)) out.push(k);
  }
  if (!out.length) throw new Error(`"${def._name ?? "a part"}" is built in no bay at all -- check every/at/skip`);
  return out;
}

// AN OVAL OF FOUR CENTRES: how the Romans set out an amphitheatre -- two tight arcs at the ends of the long axis, struck
// from (+-c, 0), and two flat ones along its sides, struck from (0, -+d), each pair meeting on the line through their two
// centres, where both have the same normal. So every ring of the building (the facade, each arcade, the podium) is the
// same four centres at another radius -- an offset of an oval of centres is an oval of the same centres -- and a bay's
// radial planes at the joint between two arcs are one plane: the bays of both arcs meet there as they meet each other.
// `oval: { c, d, ends, sides }`: the centres, and the bays in each end arc and each side arc (odd, so that a bay -- the
// main entrance -- is centred on each axis). A part's radii (rInner, rOuter, rArc) are measured on the END arcs; on the
// side arcs they are as much more as the centres are apart (K = hypot(c, d)). The bays are numbered round the whole
// oval from bay 0 on the +x axis, toward -z, and every/offset/at/skip/range pick from them as on a ring; `turn` is in
// the bays of the arc a part stands in. One geometry per kind of arc: the part comes back as itself (the ends) and
// itself with " 2" (the sides).
export function ovalOf(spec, params) {
  const c = num_(spec.c, params), d = num_(spec.d, params), nE = Math.round(num_(spec.ends, params)), nS = Math.round(num_(spec.sides, params));
  const K = Math.hypot(c, d), al = Math.atan2(d, c), be = Math.PI / 2 - al, N = 2 * (nE + nS);
  const arcs = [{ n: nE, a: 2 * al / nE, y0: Math.PI / 2 - al, C: [c, 0], side: false }, { n: nS, a: 2 * be / nS, y0: Math.PI / 2 + al, C: [0, d], side: true },
                { n: nE, a: 2 * al / nE, y0: 3 * Math.PI / 2 - al, C: [-c, 0], side: false }, { n: nS, a: 2 * be / nS, y0: 3 * Math.PI / 2 + al, C: [0, -d], side: true }];
  // bay k: which arc, its yaw (the bay's outward direction is (sin yaw, cos yaw)) and its centre
  const bay = (k) => {
    let g = (((k + (nE - 1) / 2) % N) + N) % N;
    for (const A of arcs) { if (g < A.n) return { ...A, i: g, yaw: A.y0 + (g + .5) * A.a }; g -= A.n; }
  };
  return { c, d, K, N, nE, nS, arcs, bay };
}
function ovalPart(name, def, defs, params) {
  const P = (v, d) => num_(v ?? d, params), O = ovalOf(def.oval, params);
  const picked = baysFor({ ...def, _name: name }, O.N, P);
  const out = [];
  for (const side of [false, true]) {
    const ks = picked.filter((k) => O.bay(k).side === side);
    if (!ks.length) continue;
    const A = O.arcs[side ? 1 : 0], grow = (v) => (v === undefined ? undefined : side ? P(v) + O.K : P(v));
    const sub = { ...def, oval: undefined, every: undefined, offset: undefined, only: undefined, at: [0], skip: undefined, range: undefined, place: undefined,
                  _n: 2 * Math.PI / A.a, rInner: grow(def.rInner), rOuter: grow(def.rOuter), rArc: grow(def.rArc) };
    const built = [buildPart_(name, { ...defs, [name]: sub }, params)].flat();
    for (const q of built) {
      out.push({ ...q, name: side ? q.name + " 2" : q.name, count: O.N,
                 instances: ks.flatMap((k) => { const b = O.bay(k); return q.instances.map(([a, x, y, z]) => {
                   const cs = Math.cos(b.yaw), sn = Math.sin(b.yaw);
                   return [a + b.yaw, x * cs + z * sn + b.C[0], y, -x * sn + z * cs + b.C[1]]; }); }) });
    }
  }
  return out;
}

// WHERE THE COPIES OF A STRAIGHT PART GO. `place` (or `at`) lists them as [x, y, z, yaw]; `repeat` says the
// list is a step in a series -- { count, step: [dx, dy, dz, dyaw] } -- which is how a row of vault bays, a
// colonnade or the storeys of a tower are described rather than written out.
const placements = (def, P, params) => {
  // `spiral` climbs a circle instead: `count` copies round it, each turned to follow the tangent, rising by
  // `dy` and drawing in by `dr` as it goes. A stair up a tower or between the shells of a dome is a spiral of
  // straight flights, and that is how the real ones are built.
  if (def.spiral) {
    const sp = def.spiral, n = Math.max(1, Math.round(P(sp.count)));
    const r0 = P(sp.radius), dr = P(sp.dr, 0), y0 = P(sp.y, 0), dy = P(sp.dy, 0), a0 = P(sp.turn, 0);
    const cx = P(sp.x, 0), cz = P(sp.z, 0);
    const turns = P(sp.turns, 1);                    // (`turns`: how many times round the `count` copies go -- a band wound up a column)        // what it climbs round: a drum, a dome, a tower -- rarely the origin
    // A STAIR INSIDE A DOME FOLLOWS THE DOME. Given `curve` -- the same profile the dome's meridian is struck
    // with -- the spiral reads its radius at each step's own height and draws in by that, less `inset` (the
    // shell's thickness and the width of the passage). Set out any other way the flights climb straight up
    // through the vault and finish in the air, which is exactly what they did.
    const curve = sp.curve ? domeCurve(r0, sp.curve, params) : null;
    const inset = P(sp.inset, 0);
    const radiusAt = (y) => {                       // the meridian's own radius at that height above the springing
      if (!curve) return r0;
      let best = 0;
      for (let i = 0; i + 1 < curve.length; i++) {
        const [x0, yy0] = curve[i], [x1, yy1] = curve[i + 1];
        if (x0 < -1e-9 && x1 < -1e-9) continue;     // the right half is the meridian
        if ((y >= yy0 && y <= yy1) || (y >= yy1 && y <= yy0)) {
          const f = Math.abs(yy1 - yy0) < 1e-12 ? 0 : (y - yy0) / (yy1 - yy0);
          best = Math.max(best, Math.abs(x0 + (x1 - x0) * f));
        }
      }
      return best;
    };
    const out = [];
    for (let k = 0; k < n; k++) {
      const a = a0 + k * 2 * Math.PI * turns / n;
      const r = curve ? Math.max(.6, radiusAt(k * dy) - inset) : r0 + dr * k;
      out.push([a, cx + r * Math.sin(a), y0 + dy * k, cz + r * Math.cos(a)]);   // a flight's own +x runs along the tangent at this angle
    }
    return out;
  }
  const base = def.place ?? def.at ?? [[0, 0, 0, 0]];
  let out = base.map((a) => [P(a[3], 0), P(a[0]), P(a[1], 0), P(a[2])]);
  // `repeat` a LIST is a grid: each repeats everything the one before it made (the columns of a hall, row by row)
  for (const r of def.repeat ? [def.repeat].flat() : []) {
    const n = Math.max(0, Math.round(P(r.count)));              // (0: none at all -- a one-storey wing's storeys above)
    const st = [0, 1, 2, 3].map((i) => P((r.step ?? [])[i], 0));
    out = out.flatMap(([yaw, x, y, z]) => Array.from({ length: n }, (_, k) => [yaw + st[3] * k, x + st[0] * k, y + st[1] * k, z + st[2] * k]));
  }
  return out;
};

// A dome's own numbers, read once for the dome and again for anything laid on it. `sides` left out is a ROUND
// dome: four quarters of the detail level's points, as a column's drum is.
// PLACEMENTS INSIDE PLACEMENTS: every copy of a thing (`places`, each [yaw, x, y, z]) with every piece inside it
// (`list`, in the thing's own frame) -- a colonnade's columns, a component's parts.
const composeAt = (places, list) => places.flatMap(([yaw, X, Y, Z]) => list.map(([a, x, y, z]) => {
  const c = Math.cos(yaw), s2 = Math.sin(yaw);
  return [yaw + a, x * c + z * s2 + X, y + Y, -x * s2 + z * c + Z];
}));

// ---- components: one definition used by another ---------------------------------------------------------------
// A building is made of things that are buildings of their own -- a minaret, a chhatri, a chapel tower with its
// onion, a pinnacle -- and each is written ONCE, as an asset, and `use`d wherever it stands, with its own
// params. The documents are found by path in a library, filled by `registerDocs` (the game imports the JSON) or
// by `loadUses` (a page fetches what a definition asks for, all the way down).
const LIB = new Map();
// a registered definition by its path (a component the game's library holds), or undefined
export const docOf = (path) => LIB.get(path);
export const registerDocs = (docs) => { for (const [k, v] of Object.entries(docs)) LIB.set(k, v); };
export function usesOf(doc) {
  const out = new Set();
  for (const d of Object.values(doc.parts ?? {})) {
    if (d && d.type === "component" && d.use) out.add(d.use);
    if (d && d.type === "zone" && FURNISHING.zones[d.zone]?.use) out.add(FURNISHING.zones[d.zone].use);
  }
  return [...out];
}
// the ITEMS a definition places (`item` parts), and what an item stands on and is made of (its `use`, its
// components', the materials library) -- paths under assets/, kept in the same library ("items/..." is no
// architecture path; the game registers the whole catalogue's items, a page fetches what it asks for)
const itemsOf = (doc) => {
  const own = Object.values(doc.parts ?? {}).map((d) => d?.type === "item" ? d.item : d?.type === "zone" ? FURNISHING.zones[d.zone]?.item : null).filter(Boolean);
  // (and what a period puts in their place: furnishing.json `swaps`)
  return [...new Set([...own, ...own.flatMap((p) => Object.values(FURNISHING.swaps ?? {}).map((sw) => sw[p]?.item).filter(Boolean))])];
};
const itemUses = (doc) => [...new Set([doc.use, ...(doc.parts ?? []).map((q) => q?.use)].filter((u) => typeof u === "string"))];
// fetchDoc(path) takes a path under assets/architecture; an item's is reached from there ("../items/...")
export async function loadUses(doc, fetchDoc) {
  for (const path of usesOf(doc)) {
    if (LIB.has(path)) continue;
    const sub = await fetchDoc(path);
    LIB.set(path, sub);
    await loadUses(sub, fetchDoc);
  }
  const items = itemsOf(doc);
  if (items.length && !LIB.has("items/materials")) LIB.set("items/materials", await fetchDoc("../items/materials"));
  const item = async (path) => {
    if (LIB.has(path)) return;
    const sub = await fetchDoc("../" + path);
    LIB.set(path, sub);
    for (const u of itemUses(sub)) await item(u);
  };
  for (const path of items) await item(path);
}
// AN ITEM, built (items.js) out of the library, once per path, seed, params and materials -- the assembly takes its
// box and its markers from it, architecture.js its triangles
const ITEMS = new Map();
export function itemOf({ path, seed = 1, params = {}, materials = null }) {
  const key = JSON.stringify([path, seed, params, materials]);
  if (!ITEMS.has(key)) {
    if (!LIB.has(path)) throw new Error(`item "${path}" is not loaded (registerDocs / loadUses)`);
    ITEMS.set(key, buildItem(path, LIB, LIB.get("items/materials")?.materials ?? {}, { seed, params, materials: materials ?? {} }));
  }
  return ITEMS.get(key);
}
const NOTHING = () => ({ position: new Float32Array(0), index: new Uint16Array(0) });

// A PLAN's numbers, evaluated: { rect: [w, l], chamfer } | { sides, radius } | { points }
const planOf = (pl, P) => ({
  ...(pl.points ? { points: pl.points.map(([x, z]) => [P(x), P(z)]) }
    : pl.sides !== undefined ? { sides: P(pl.sides), radius: P(pl.radius) }
    : { rect: [P(pl.rect[0]), P(pl.rect[1])], chamfer: P(pl.chamfer, 0) }),
  ...(pl.split ? { split: Object.fromEntries(Object.entries(pl.split).map(([k, v]) => [k, v.map((x) => P(x))])) } : {}) });

// A FACE'S OPENINGS, laid out along a face `L` long: a pattern (centred on the face -- the rhythm says how wide
// it is) or a list of openings measured from the face's middle.
function laidOut(spec, L, P, params) {
  if (!spec) return [];
  if (spec.pattern) {
    const o = patternOpenings(spec, params), shift = (L - o.width) / 2;
    if (shift < -1e-9) throw new Error(`a face ${L.toFixed(2)}m long cannot hold a pattern ${o.width.toFixed(2)}m long`);
    return o.openings.map((q) => ({ ...q, at: q.at + shift }));
  }
  return spec.map((k) => ({ ...openingOf(k, P, params), at: L / 2 + P(k.at, 0) }));
}

// A FACE'S TIERS: a list of { h, openings } bands (the last one takes whatever height is left if it gives none),
// or a plain openings spec, which is one band the whole height
function tiersOf(spec, H, L, P, params) {
  // (a list of TIERS -- each { h, openings }, the last one's h the rest -- or of openings: a tier is known by its
  //  `openings`, not only its `h`, or a single tier, the whole face, was read as a list of openings: a court of one storey)
  const list = Array.isArray(spec) && spec.length && (spec[0].h !== undefined || spec[0].openings !== undefined) ? spec : [{ openings: spec }];
  let used = 0;
  return list.map((t, k) => {
    const h = t.h !== undefined ? P(t.h) : H - used;
    used += h;
    if (k === list.length - 1 && Math.abs(used - H) > 1e-6) throw new Error(`a face's tiers add up to ${used.toFixed(2)}m, not its ${H}m`);
    return { h, openings: glazed(laidOut(t.openings, L, P, params), flagOf(t.glass, params)), ...lombardOf(t.lombard, params) };
  });
}

// ONE OPENING from its definition: centre `at`, `width`, `sill`, `springing`, its `head` and (if it has one) its
// `foot` -- the profile below the sill that makes a round window round.
const openingOf = (k, P, params) => ({
  at: P(k.at), width: P(k.width), sill: P(k.sill, 0), springing: P(k.springing ?? k.sill, 0),
  head: headOf(k.head, params), ...(k.foot ? { foot: headOf(k.foot, params) } : {}), ...glassOf(k, params), ...traceryOf(k, params), ...wimpergOf(k, params), ...surroundOf(k, params) });
// TRACERY in a window (tracery.js): `tracery: true` (its lights as many as its span allows), a number of lights, or
// { style (geometric, perpendicular, bars: a sash's glazing bars), lights, foils, bar, depth, pane, cols, rows }
function traceryOf(spec, params) {
  const t = spec?.tracery;
  if (t === undefined || t === false) return {};
  if (t === true) return { tracery: {} };
  if (typeof t !== "object") return { tracery: { lights: num_(t, params) } };
  return { tracery: Object.fromEntries(Object.entries(t).map(([k, v]) => [k, k === "foils" ? flagOf(v, params) : k === "style" ? wordOf(v, params) : num_(v, params)])) };
}

// A SURROUND round an opening (surround.js): `surround: true`, or { band, depth, sill, head, pediment, pitch, keystone }
// -- `head` pediment | cornice | false, `pediment` triangular | segmental | alternate (words or params holding one);
// or { style: "romanesque", orders, band, depth, shafts }: the opening recessed in orders instead of framed
function surroundOf(spec, params) {
  const w = typeof spec?.surround === "string" ? flagOf(spec.surround, params) : spec?.surround;   // (or a flag over the params)
  if (w === undefined || w === false) return {};
  if (w === true) return { surround: {} };
  return { surround: Object.fromEntries(Object.entries(w).filter(([k]) => !k.startsWith("_"))
    .map(([k, v]) => [k, ["sill", "keystone", "side", "shafts"].includes(k) ? flagOf(v, params) : ["head", "pediment", "style"].includes(k) ? (v === false ? false : wordOf(v, params)) : num_(v, params)])) };
}
// A LOMBARD BAND on a face (lombard.js): `lombard: true` or { arch, band, depth, lesene, bay, drop, foot, lesenes, side }
// -- on a tier, or on a wall or an enclosure (its top tier on every face; a tier's own `lombard: false` keeps it bare)
// (`on`: a flag over the params -- a component that has the band only if asked, `"on": "lombard"`; a bare flag the same)
function lombardOf(spec, params) {
  if (spec === undefined || spec === null) return {};
  if (typeof spec !== "object") spec = { on: spec };
  if (spec.on !== undefined && !flagOf(spec.on, params)) return { lombard: false };
  return { lombard: Object.fromEntries(Object.entries(spec).filter(([k]) => !k.startsWith("_") && k !== "on")
    .map(([k, v]) => [k, ["lesenes", "side"].includes(k) ? flagOf(v, params) : k === "clear" ? v.map((r) => r.map((q) => num_(q, params))) : num_(v, params)])) };
}
const withLombard = (tiers, def, params) => def.lombard === undefined ? tiers
  : tiers.map((t, k) => (k === tiers.length - 1 && t.lombard === undefined ? { ...t, ...lombardOf(def.lombard, params) } : t));
// A WIMPERG over an opening (wimperg.js): `wimperg: true`, or { pitch, coping, depth, crockets, finial, field,
// shafts, side } -- the flags may be expressions, as every number may
function wimpergOf(spec, params) {
  const w = spec?.wimperg;
  if (w === undefined || w === false) return {};
  if (w === true) return { wimperg: {} };
  return { wimperg: Object.fromEntries(Object.entries(w).filter(([k]) => !k.startsWith("_"))
    .map(([k, v]) => [k, ["crockets", "finial", "field", "shafts", "side"].includes(k) ? flagOf(v, params) : num_(v, params)])) };
}

// COURSES on a wall or an enclosure (courses.js): `courses: true` (a plinth, a string course at every tier joint, a
// cornice), or { plinth, strings, cornice }, each false, true or { h, out, profile } -- `strings` may be a list of
// heights instead -- and every number an expression. Built as a part of their own beside the wall: "<name> courses"
// -- and on a SOLID, a box or a prism: a plinth's mouldings run round its own outline, closed (an Indian temple's
// adhishthana, khura to kapota; a podium's base and crown), the outline's faces counted as an enclosure's are
function coursesSpec(v, params) {
  if (typeof v === "string") v = flagOf(v, params);     // (a flag over the params: a component dressed or plain as it is asked)
  if (v === undefined || v === false) return null;
  if (v === true) return true;
  const ev = (c) => Object.fromEntries(Object.entries(c).filter(([k]) => !k.startsWith("_")).map(([k, x]) => [k, k === "profile" ? wordOf(x, params) : num_(x, params)]));
  // (a list: the courses outright -- courses.js coursesOf; `{ list, skip, clear }` the same with the faces it keeps off)
  if (Array.isArray(v) || Array.isArray(v.list)) return (v.list ?? v).map(ev);
  const one = (c) => (c === undefined || c === true ? c : c === false ? false
    : Array.isArray(c) ? c.map((y) => num_(y, params))
    : Object.fromEntries(Object.entries(c).filter(([k]) => !k.startsWith("_")).map(([k, x]) => [k, k === "profile" ? wordOf(x, params) : k === "at" ? x.map((y) => num_(y, params)) : num_(x, params)])));
  return { plinth: one(v.plinth), strings: one(v.strings), cornice: one(v.cornice) };
}
// THE PLAN OF A WALL'S MOULDINGS -- its courses and its orders, each order sized from the storeys it spans and standing
// on what course runs under its foot: { courses, sized, joints } (null: none). The wall's own openings are drawn
// knowing it, so a window's pediment stays under the entablature over it (the tiers' `top`, withOrderTops)
function orderPlan(def, params, H, t, tierList) {
  let spec = coursesSpec(def.courses, params);
  // THE ORDERS (order.js): each from its storey's foot to the top of the last it spans -- no string course at a joint
  // within it or at its top (its entablature is that moulding), no cornice over one that crowns the wall
  const foots = [0]; for (const b of tierList[0] ?? []) foots.push(foots[foots.length - 1] + b.h);
  // (an order of kind "none" is none: a component's storey left plain unless the building asks for an order there)
  const orders = (def.orders ?? []).filter((o) => wordOf(o.kind ?? "tuscan", params) !== "none").map((o) => {
    const tier = Math.round(num_(o.tier ?? 0, params)), span = Math.max(1, Math.round(num_(o.span ?? 1, params)));
    return { kind: wordOf(o.kind ?? "tuscan", params), y0: foots[tier] ?? 0, y1: foots[Math.min(foots.length - 1, tier + span)] ?? H,
             ends: o.ends === undefined ? true : flagOf(o.ends, params), ...(o.proj !== undefined ? { proj: num_(o.proj, params) } : {}) };
  });
  if (!spec && !orders.length) return null;
  const within = (y) => orders.some((o) => y > o.y0 + 1e-6 && y < o.y1 + 1e-6);
  if (orders.some((o) => o.y1 > H - 1e-6)) spec = { ...(spec === true || !spec ? {} : spec), cornice: false };
  if (spec?.strings && typeof spec.strings === "object") spec = { ...spec, strings: Array.isArray(spec.strings) ? spec.strings.filter((y) => !within(y))
    : spec.strings.at ? { ...spec.strings, at: spec.strings.at.filter((y) => !within(y)) } : spec.strings };
  const joints = [...new Set(tierList.flatMap((tiers) => { let y = 0; return tiers.slice(0, -1).map((b) => (y += b.h)); }))].filter((y) => !within(y));
  const courses = spec ? coursesOf(spec, H, t, joints) : [];
  // each order's pilasters stand on what moulding runs under their foot (a string course, the plinth), and its
  // entablature runs round as a course of its own section
  const sized = orders.map((o) => {
    const under = courses.filter((c) => c.y <= o.y0 + 1e-6 && c.y + c.h > o.y0).sort((a, b) => b.y + b.h - a.y - a.h)[0];
    const foot = under ? Math.max(o.y0, under.y + under.h) : o.y0;
    const s = orderSize(o.kind, ORDERS[o.kind], o.y1 - foot, o);
    courses.push({ y: foot + s.col, h: s.ent, out: Math.max(...s.profile.map(([q]) => q)), pts: s.profile });
    return { ...o, foot, yb: under ? under.y : foot, s };
  });
  return { courses, sized };
}
// (each tier an order spans keeps what dresses its openings -- a surround's pediment, a wimperg -- under the order's
//  entablature: its `top`, over the tier's own foot)
const withOrderTops = (plan, tiers) => {
  if (!plan?.sized.length) return tiers;
  let y = 0;
  return tiers.map((b) => {
    const y0 = y; y += b.h;
    const tops = plan.sized.filter((o) => y0 >= o.y0 - 1e-6 && y <= o.y1 + 1e-6).map((o) => o.foot + o.s.col - y0);
    return tops.length ? { ...b, top: Math.min(...tops) } : b;
  });
};
// THE LINTELS a face's openings are spanned by: every opening with a FLAT head is one beam over it, its underside at
// the springing -- [{ at: [x, y, z], span }] in the part's frame, along `line` (an outline, `closed`, or a wall's run;
// `tierList[i]` segment i's tiers), for check.js lintels: stone or timber, a beam has a length it can't be made past
// (`t`: the wall's thickness -- what stands in its opening, a pillar under the beam, is looked for through it)
const lintelsOf = (line, tierList, t, closed = false) => {
  const out = [];
  for (let i = 0; i < (closed ? line.length : line.length - 1); i++) {
    const A = line[i], B = line[(i + 1) % line.length], L = Math.hypot(B[0] - A[0], B[1] - A[1]);
    let y0 = 0;
    for (const b of tierList[Math.min(i, tierList.length - 1)] ?? []) {
      for (const o of wallFace(L, b.h, b.openings ?? []).openings) {
        if ((o.head?.profile ?? "semicircular") !== "flat") continue;
        const f = (o.x0 + o.x1) / 2 / L;
        out.push({ at: [A[0] + (B[0] - A[0]) * f, y0 + o.springing, A[1] + (B[1] - A[1]) * f], span: o.x1 - o.x0, e: [(B[0] - A[0]) / L, (B[1] - A[1]) / L], t });
      }
      y0 += b.h;
    }
  }
  return out;
};
// (a solid's: no openings in its faces, and no thickness for the defaults to go by -- a metre's)
const solidCourses = (part, def, params, H, pts) => def.courses === undefined ? part
  : withCourses(part, def, params, H, 1, pts, pts.map(() => [{ h: H, openings: [] }]), true);
const withCourses = (parts, def, params, H, t, line, tierList, closed = false, xmap = [], plan = orderPlan(def, params, H, t, tierList)) => {
  if (!plan) return parts;
  const { courses, sized } = plan;
  const segs = closed ? line.length : line.length - 1;
  // (`clear`: { face: [[x0, x1], ...] } -- stretches along a face, from its start, it stops short of at every height: where
  //  a tower or a wing stands against it, so the moulding comes to that block's side and ends there)
  const clear = def.courses?.clear ?? {};
  const gaps = Array.from({ length: segs }, (_, i) => {
    const A = line[i], B = line[(i + 1) % line.length];
    const f = xmap[i], own = faceGaps(f ? f.L : Math.hypot(B[0] - A[0], B[1] - A[1]), tierList[Math.min(i, tierList.length - 1)])
      .map((q) => (f ? { ...q, x0: f.x(q.x1), x1: f.x(q.x0) } : q));      // (an inner face: its openings come through)
    const lab = line.labels?.[i], cl = clear[line.faces?.[i] ?? i] ?? (lab ? clear[lab] ?? clear[lab.split(":")[0]] : undefined) ?? [];
    // (a stretch may give [x0, x1, y0, y1]: kept clear only that high -- the foot of a face a lower block stands against,
    //  its cornice running on over the neighbour's roof)
    return [...own, ...cl.map(([x0, x1, y0, y1]) => ({ x0: num_(x0, params), x1: num_(x1, params), y0: y0 === undefined ? -Infinity : num_(y0, params), y1: y1 === undefined ? Infinity : num_(y1, params) }))];
  });
  // (`skip`: faces by number or label -- "main:1" -- or family -- "main" -- that it does not run along)
  const sk = (def.courses?.skip ?? []).map(String), labels = line.labels ?? [];
  const skip = new Set(gaps.map((_, i) => i).filter((i) => sk.includes(String(line.faces?.[i] ?? i)) || (labels[i] && (sk.includes(labels[i]) || sk.includes(labels[i].split(":")[0])))));
  const m = coursesMesh(mesh(), line, courses, { closed, gaps, skip });
  // (the corners: each one's turn -- the tangent of half of it, negative where the line turns in -- and whether the
  //  pilasters fold round it: a shallow outer corner between two faces that both carry the order)
  const dir = (i) => { const A = line[i % line.length], B = line[(i + 1) % line.length], L = Math.hypot(B[0] - A[0], B[1] - A[1]); return [(B[0] - A[0]) / L, (B[1] - A[1]) / L]; };
  const turnAt = (i) => {                                // the corner at the start of segment i
    const a = dir((i + segs - 1) % segs), b = dir(i), th = Math.acos(Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1])));
    return Math.tan(th / 2) * (a[0] * b[1] - a[1] * b[0] < 0 ? 1 : -1);    // (the outside on the left: a right turn is an outer corner)
  };
  const endOf = (o, i, atEnd) => {
    const j = atEnd ? i + 1 : i;                         // (the corner's index: the start of the segment after it)
    if (!o.ends) return false;
    if (!closed && (j <= 0 || j >= segs)) return true;   // (a free end of a run)
    const k = turnAt(j % segs);
    return !skip.has((atEnd ? i + 1 : i + segs - 1) % segs) && k > 0 && k < .43 ? "fold" : true;
  };
  for (const o of sized) gaps.forEach((gs, i) => {
    if (skip.has(i)) return;
    const A = line[i], B = line[(i + 1) % line.length], L = Math.hypot(B[0] - A[0], B[1] - A[1]), e = [(B[0] - A[0]) / L, (B[1] - A[1]) / L];
    const ops = gs.filter((q) => q.y0 < o.foot + o.s.col && q.y1 > o.foot);
    const { spots, folds } = pilasterSpots(L, ops, o.s, { ends: [endOf(o, i, false), endOf(o, i, true)] });
    for (const x of spots) pilasterMesh(m, A, e, [-e[1], e[0]], x, o.foot, o.s, 0, 0, o.yb);
    for (const x of folds) pilasterMesh(m, A, e, [-e[1], e[0]], x, o.foot, o.s, x > 0 ? -1 : 1, turnAt(x > 0 ? (i + 1) % segs : i), o.yb);
  });
  const list = [parts].flat();
  return m.counts.tris ? [...list, { name: list[0].name + " courses", geometry: m.arrays(), instances: list[0].instances, kind: "moulding", shell: true }] : parts;
};

// WHETHER AN OPENING IS GLAZED is said once for a whole kind of opening, not opening by opening: `glass: true`
// or `false` on an openings spec (a pattern, or one entry of a list), on a TIER, or on the PART -- the most
// particular wins. Said nowhere, an opening standing over the floor (a sill over 30cm) is a window and is glazed,
// and a door or an arcade is left open (build.js glassPanes). A belfry, a gallery, a loggia says `glass: false`.
// (the flag may be an expression over the params -- a component's `glazed` -- as every number may)
const flagOf = (v, params) => v === undefined ? undefined : typeof v === "string" ? num_(v, params) !== 0 : !!v;
function glassOf(spec, params) { const f = flagOf(spec?.glass, params); return f === undefined ? {} : { glass: f }; }
const glazed = (openings, flag) => flag === undefined ? openings : openings.map((o) => (o.glass !== undefined ? o : { ...o, glass: !!flag }));

// A PART AND ITS GLASS: the panes in its windows (build.js glassPanes) as a part of their own, drawn in glass, or
// the part alone if it has no windows (or says `glass: false`)
// (and the TRACERY in them, glazed or open, as another: stone; and the WIMPERGS over them, a third)
const withGlass = (part, g) => (!g || (!g.counts.tris && !g.tracery?.counts.tris && !g.wimperg?.counts.tris && !g.surround?.counts.tris)) ? part
  : [part, ...(g.counts.tris ? [{ name: part.name + " glass", geometry: g.arrays(), instances: part.instances, kind: "glass", shell: true }] : []),
     ...(g.tracery?.counts.tris ? [{ name: part.name + " tracery", geometry: g.tracery.arrays(), instances: part.instances, kind: "tracery", shell: true }] : []),
     ...(g.wimperg?.counts.tris ? [{ name: part.name + " wimperg", geometry: g.wimperg.arrays(), instances: part.instances, kind: "wimperg", shell: true }] : []),
     ...(g.surround?.counts.tris ? [{ name: part.name + " surrounds", geometry: g.surround.arrays(), instances: part.instances, kind: "moulding", shell: true }] : [])];

// A groin vault's own numbers, read once for the vault and again for the ribs laid under it
function groinOf(def, P, params) {
  const width = P(def.width), length = P(def.length), springing = P(def.springing);
  const across = headOf(def.across ?? def.head, params), alongH = headOf(def.along ?? def.head, params);
  return { width, length, springing, curveX: archCurve(width / 2, across), curveZ: archCurve(length / 2, alongH) };
}

function domeOf(name, def, P, params, build = true) {
  const radius = P(def.radius), thickness = P(def.thickness, 0), oculus = P(def.oculus, 0);
  const share = Math.max(.02, Math.min(1, P(def.sweep, 1)));      // 1 a whole dome, .5 a SEMIDOME (an apse's conch)
  // COFFERS are cut into the soffit (build.js cofferedSurface): `count` round, `rows` up, between `from` and `to`
  // (shares of the inner meridian's length), `depth` deep in `steps` steps. A round dome then takes as many
  // faces as makes each coffer a whole number of them.
  const cf = def.coffers ? { count: Math.round(P(def.coffers.count)), rows: Math.round(P(def.coffers.rows)),
    from: P(def.coffers.from, .05), to: P(def.coffers.to, .7), depth: P(def.coffers.depth), steps: Math.round(P(def.coffers.steps, 1)),
    frame: P(def.coffers.frame, .12), step: P(def.coffers.step, .07), kv: Math.round(P(def.coffers.kv, 1)),
    toward: def.coffers.toward !== undefined ? P(def.coffers.toward) : undefined } : null;
  const dd = detailFor(params, radius);                  // (its detail by its size)
  const perCoffer = cf ? Math.max(1, Math.round(4 * dd * share / cf.count)) : 1;
  const sides = Math.max(3, Math.round(def.sides !== undefined ? P(def.sides)
                                     : cf ? cf.count * perCoffer / share : 4 * dd));
  const curve = domeCurve(radius, def.head, params);
  if (cf && !(thickness > 0)) throw new Error("coffers are cut into a shell -- a skin has no thickness to cut them in");
  // `turn` (in faces): -0.5 puts the corners on the axes, as a dome standing on pendentives needs
  const turn = P(def.turn, 0);
  // `door` { width, height, at }: a doorway cut in its foot (build.js domeShell)
  const door = def.door ? { width: P(def.door.width), height: P(def.door.height), ...(def.door.at !== undefined ? { at: P(def.door.at) } : {}) } : null;
  const m = build ? domeShell(mesh(), { sides, sweep: share, turn, oculus, thickness, curve, base: 0, cap: def.cap !== false, coffers: cf, door }) : null;
  return { m, curve, sides, sweep: share, turn, oculus, instances: placements(def, P, params), rise: Math.max(...curve.map(([, y]) => y)) };
}

// WHERE A PART'S TOP IS: a dome's crown (its placement plus the meridian's rise), or the head of anything with a
// height -- so a finial, a lantern or a cross can stand ON something rather than at a guessed height (`atop`)
// `r`: WHERE A DOME HAS NARROWED TO THAT RADIUS -- a lantern `r` wide stands on the dome's surface there, not on its
// tip in the air (a pointed or onion dome is narrower than its lantern for its last metres)
// a `basilica` part's measures, its expressions evaluated (gothic.js basilica reads them)
function basilicaOf(def, P, params) {
  const D = { bays: 6, bayLen: 6, naveW: 12, aisleW: 8, apse: 5, t: 1.2, aisleT: 1.2, spring: 8, shaft: .22, pierR: .9,
              vaultT: .5, clerSpring: 1.5, pitch: 55, aislePitch: 22, overhang: .5, lights: 4, aisleSill: 2.5, aisleWin: 3,
              buttressW: 1.6, buttressD: 2.8, flyW: .8, ribW: .32, ribD: .34 };
  const d = Object.fromEntries(Object.entries(D).map(([k, v]) => [k, P(def[k], v)]));
  for (const k of ["arcadeRise", "vaultRise", "arm", "transeptT", "aisles", "flyerStages", "aisleDrop"]) if (def[k] !== undefined) d[k] = P(def[k]);
  if (def.transept) d.transept = def.transept.map((v) => P(v));
  d.flyers = def.flyers === undefined ? true : flagOf(def.flyers, params);
  d.pinnacles = def.pinnacles === undefined ? true : flagOf(def.pinnacles, params);
  d.tracery = def.tracery === undefined ? true : flagOf(def.tracery, params);
  d.wimpergs = def.wimpergs === undefined ? false : flagOf(def.wimpergs, params);
  d.hall = def.hall === undefined ? false : flagOf(def.hall, params);
  for (const k of ["skipAisle", "skipOuter", "skipButtress"]) d[k] = (def[k] ?? []).map(([f, to]) => [P(f), P(to)]);
  // (the Romanesque dress: a Lombard band on the clerestory and on the aisle wall -- `aisleLombard` if it differs --
  //  and the windows' surround: lombard.js, surround.js)
  d.lombard = lombardOf(def.lombard, params).lombard;
  d.aisleLombard = def.aisleLombard === undefined ? d.lombard : lombardOf(def.aisleLombard, params).lombard;
  d.surround = surroundOf(def, params).surround;
  return d;
}
// a `samvarana` part's measures (shikhara.js)
function samvaranaOf(def, P, params) {
  const a = P(def.width) / 2;
  return { a, rise: P(def.rise), tiers: P(def.tiers, 5), top: P(def.top, .3), rathas: P(def.rathas, 3), step: P(def.step, a * .06),
           bhadra: P(def.bhadra, .34), bells: def.bells === undefined ? true : flagOf(def.bells, params), ribs: Math.max(8, 4 * detailOf(params)),
           len: def.length === undefined ? 1 : P(def.length) / (2 * a) };
}
// a `shikhara` part's measures (shikhara.js)
function shikharaOf(def, P, params) {
  const a = P(def.width) / 2;
  return { a, H: P(def.height), rathas: P(def.rathas, 5), step: P(def.step, a * .08), bhadra: P(def.bhadra, .3), top: P(def.top, .55),
           bend: P(def.bend, 1.7), bhumis: P(def.bhumis, 7), band: P(def.band, .035), bandH: P(def.bandH, .22), nest: P(def.nest, 1),
           ribs: Math.max(8, 4 * detailOf(params)),
           tiers: (def.tiers ?? []).map((t) => ({ scale: P(t.scale), lift: P(t.lift, 0), out: P(t.out, .45) })),
           corners: def.corners ? { scale: P(def.corners.scale), at: [].concat(def.corners.at ?? [0]).map((v) => P(v)) } : null };
}
function topOf(name, defs, params, r = 0, level = null) {
  const d = defs[name], P = (v, dd) => num_(v ?? dd, params);
  if (!d) throw new Error(`"atop": no part named "${name}"`);
  // (and if it stands `atop` another in turn, from that one's top: a ball on a roof on a lantern on a dome)
  const y0 = (placements(d, P, params)[0] ?? [0, 0, 0, 0])[2] + P(d.y, 0)
           + (d.atop ? topOf(d.atop, defs, params, d.atopR !== undefined ? P(d.atopR) : 0, d.atopLevel) : 0);
  // (a basilica's heights are its own: the level asked for -- its eaves unless said)
  if (d.type === "basilica") return y0 + basilicaLevels(basilicaOf(d, P, params))[level ?? "wallTop"];
  if (d.type === "shikhara") return y0 + shikharaHeight(shikharaOf(d, P, params));   // (to its kalasha's tip)
  if (d.type === "samvarana") return y0 + samvaranaHeight(samvaranaOf(d, P, params));
  if (d.type === "helm") {   // (a helm's point: helm.js)
    const n = Math.round(P(d.sides, 4)), s = Math.sin(Math.PI / n), half = d.width !== undefined ? P(d.width) / 2 : P(d.radius) * s;
    return y0 + half * Math.tan(P(d.pitch, 60) * Math.PI / 180) / (s * s);
  }
  if (d.type !== "dome") return y0 + P(d.height, 0);
  const { curve, rise } = domeOf(name, d, P, params, false);
  if (!(r > 0)) return y0 + rise;
  let best = null;                                        // the highest point of the meridian at radius r
  for (let i = 0; i + 1 < curve.length; i++) {
    const [x0, ya] = curve[i], [x1, yb] = curve[i + 1];
    if (x0 < 0 && x1 < 0) continue;
    if ((x0 - r) * (x1 - r) > 0 || x0 === x1) continue;
    const y = ya + (yb - ya) * (r - x0) / (x1 - x0);
    if (best === null || y > best) best = y;
  }
  return y0 + (best ?? rise);
}

// the edges round a WELL in a floor at height h, the way across each into the hole -- railingsFor rails them where
// they drop, as a landing's free edges (over the treads just below the arrival they do not)
const wellEdges = (well, h) => well.pts.map((a, i) => {
  const b = well.pts[(i + 1) % well.pts.length], mx = (a[0] + b[0]) / 2, mz = (a[1] + b[1]) / 2;
  const [cx, cz] = [well.cx, well.pts.reduce((s, q) => s + q[1], 0) / well.pts.length], l = Math.hypot(cx - mx, cz - mz) || 1;
  return { a: [a[0], h, a[1]], b: [b[0], h, b[1]], n: [(cx - mx) / l, (cz - mz) / l] };
});

// THE FLOOR A STAIR ARRIVES ON, where the building gives it none (`arrive` on a staircase, a flight or a spiral): a
// stair leads somewhere, and one standing on its own is given the floor at its top it would reach in a house -- a slab
// `thick` deep (the stair's soffit) on square posts `post` wide, at its corners and every `span` metres along its sides,
// standing where the stair stands: built from the ground up, nothing at the top left hanging. A straight stair's floor
// begins at the far edge of each landing it ends on (top landings on one line share one floor), `depth` deep and `width`
// wide (their span and a metre either side); a spiral's is a square round its top, `depth` past the treads every way,
// with a WELL the stair comes up through (its sides clear of the treads' outer edge). Its free edges are railed as a
// landing's are (railingsFor), wherever a drop opens beside them -- the well round, except over the treads just below.
function arrivalFloor(name, def, P, params, { tops = [], spiral = null, soffit }) {
  const A = def.arrive === true ? {} : def.arrive;
  const thick = P(A.thick, soffit), post = P(A.post, .35), span = P(A.span, 3.5), depth = P(A.depth, 2.5), inset = post / 2 + .05;
  const floors = [];                                      // { pts (corners at the top), well, h }
  if (spiral) {
    const N = 4 * detailOf(params), r = (spiral.R + .05) / Math.cos(Math.PI / N), h = spiral.R + depth;
    floors.push({ pts: [[-h, -h], [h, -h], [h, h], [-h, h]], h: spiral.top, well: wellPoints({ at: [0, 0], radius: r, sides: N }) });
  } else {
    // (landings ending on one line, facing one way, at one height: one floor across them all)
    const groups = new Map();
    for (const t of tops) {
      const ol = Math.hypot(t.out[0], t.out[1]), o = [t.out[0] / ol, t.out[1] / ol], d = t.a[0] * o[0] + t.a[2] * o[1];
      const key = [o[0], o[1], d, t.a[1]].map((v) => v.toFixed(3)).join();
      if (!groups.has(key)) groups.set(key, { o, d, h: t.a[1], ts: [] });
      groups.get(key).ts.push(...[t.a, t.b].map((p) => p[2] * o[0] - p[0] * o[1]));   // (along the line: u = (-o.z, o.x))
    }
    for (const { o, d, h, ts } of groups.values()) {
      const lo = Math.min(...ts), hi = Math.max(...ts), W = P(A.width, hi - lo + 2), mid = (lo + hi) / 2;
      const at = (t, s) => [-o[1] * t + o[0] * (d + s), o[0] * t + o[1] * (d + s)];
      floors.push({ pts: [at(mid - W / 2, 0), at(mid + W / 2, 0), at(mid + W / 2, depth), at(mid - W / 2, depth)], h });
    }
  }
  const sm = mesh(), pm = mesh(), edges = [];
  for (const f of floors) {
    const pts = planPoints({ points: f.pts });
    prismMesh(sm, pts, f.h - thick, f.h, f.well);
    const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length, cz = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    pts.forEach((a, i) => {
      const b = pts[(i + 1) % pts.length], dx = b[0] - a[0], dz = b[1] - a[1], l = Math.hypot(dx, dz);
      const n = (dz * ((a[0] + b[0]) / 2 - cx) - dx * ((a[1] + b[1]) / 2 - cz)) > 0 ? [dz / l, -dx / l] : [-dz / l, dx / l];
      edges.push({ a: [a[0], f.h, a[1]], b: [b[0], f.h, b[1]], n });
      // the posts along it: at its start (a corner) and every `span` on, set in from both sides by half a post and 5cm
      const k = Math.max(1, Math.ceil(l / span));
      for (let q = 0; q < k; q++) {
        const t = q / k, along = q === 0 ? inset : 0;
        const x = a[0] + dx * t + dx / l * along - n[0] * inset, z = a[1] + dz * t + dz / l * along - n[1] * inset;
        box(pm, x - post / 2, x + post / 2, 0, f.h - thick, z - post / 2, z + post / 2);
      }
    });
    if (f.well) edges.push(...wellEdges(f.well, f.h));
  }
  const instances = placements(def, P, params);
  // (the posts first: they are set up before the slab is laid on them)
  return [{ name: name + " posts", geometry: pm.arrays(), instances, kind: "column", stairPart: name },
          { name: name + " floor", geometry: sm.arrays(), instances, kind: "prism", walked: true, edges, railing: def.railing, stairPart: name }];
}

// A RAILING WHERE A STAIR'S SIDE IS OPEN. Every stair carries its walking path (every tread's middle, its width); along
// each side, just past the tread's edge, at knee and at chest height, the assembled building is asked whether stone
// is there -- a wall the stair hugs, the newel, the turret round a spiral. Where it is not, the side gets a railing,
// in the building's own kind (`railing: { type, height }` on the definition, a stair's own `railing` overriding it,
// `false` for none): "balusters" (a post at every tread and a handrail), "iron" (thin posts, a handrail, a middle
// rail), "stone" (a parapet, solid, sloping with the flight). A railing is its own part, "<stair> railing", in the
// building's frame -- a wall to the walk (the game's wall field reads it), a thing to lean on.
function railingsFor(parts, spec, params) {
  // (a spiral in its turret, round its newel, is walled both sides all the way and gets none; one standing free -- in an
  //  open well, round no post, under a floor it comes up through -- is railed where it is open, as a flight is)
  const stairs = parts.filter((p) => (p.path || p.edges) && p.kind !== "railing" && p.railing !== false);
  if (!stairs.length) return [];
  const { cells } = solidIndex({ parts });
  const out = [];
  const post = (m, p, s, y0, y1) => box(m, p[0] - s, p[0] + s, y0, y1, p[2] - s, p[2] + s);
  // a rail swept along a stretch of points: its section `t` across (toward n) and from h0 to h1 over the line, one
  // solid from end to end (no faces inside it where one tread's piece would meet the next)
  const rail = (m, pts, ns, t, h0, h1) => {
    const ring = pts.map((a, i) => [[a[0], a[1] + h0, a[2]], [a[0] + ns[i][0] * t, a[1] + h0, a[2] + ns[i][1] * t],
                                    [a[0] + ns[i][0] * t, a[1] + h1, a[2] + ns[i][1] * t], [a[0], a[1] + h1, a[2]]].map((q) => m.vert(q[0], q[1], q[2])));
    const a = pts[0], b = pts[1], n0 = ns[0];
    const flip = ((b[0] - a[0]) * n0[1] - (b[2] - a[2]) * n0[0]) < 0;     // (which way round the section winds)
    const q = flip ? (w, x, y, z) => m.quad(z, y, x, w) : (w, x, y, z) => m.quad(w, x, y, z);
    for (let i = 0; i + 1 < ring.length; i++) for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4; q(ring[i][k], ring[i + 1][k], ring[i + 1][k2], ring[i][k2]); }
    const e = ring.length - 1;
    q(ring[0][0], ring[0][1], ring[0][2], ring[0][3]); q(ring[e][3], ring[e][2], ring[e][1], ring[e][0]);   // (its ends wound as its sides are)
  };
  // is the side of a walk open at p -- `out` the way across the edge, `half` from p out to the edge: no stone just past
  // the edge at knee and chest height, and the floor beside more than half a metre below (the flights and the landings ask
  // it alike)
  let asker = null;
  const openBeside = (p, out, half) => {
    const x = p[0] + out[0] * (half + .12), z = p[2] + out[1] * (half + .12);
    // (stone beside: at the tread's own level, or at both knee and chest -- a floor slab passing OVERHEAD beside a
    //  flight, met at the knee on one tread and at the chest on another, is no wall: the railing ran broken there)
    const hit = (h) => [.12, .35].some((o) => insideOf(cells, p[0] + out[0] * (half + o), p[1] + h, p[2] + out[1] * (half + o), asker).length > 0);
    if (hit(.15) || (hit(.6) && hit(1.2))) return false;
    let below = 0;                                     // (the highest floor beside, under the walk's height)
    for (const t of cells.get(cellOf(x, z)) ?? []) {
      if (t.part.name === asker) continue;
      const h = heightOver(t, x, z);
      if (h !== null && h <= p[1] + .1 && h > below) below = h;
    }
    return p[1] - below > .5;
  };
  for (const st of stairs) {
    asker = st.name;
    const kind = { ...spec, ...(typeof st.railing === "object" ? st.railing : {}) };
    const type = wordOf(kind.type ?? "balusters", params), H = num_(kind.height ?? .95, params);
    const m = mesh(), ml = mesh();          // (the landings' railings a part of their own: they meet the flights' end to end)
    const walled = { [-1]: true, [1]: true };   // (a side with stone beside every tread, in every placement)
    for (const [yaw, X, Y, Z] of st.instances) {
      const c = Math.cos(yaw), sn = Math.sin(yaw);
      const W = ([x, y, z]) => [x * c + z * sn + X, y + Y, -x * sn + z * c + Z];
      // the runs of treads (a landing, or a jump, ends one)
      const runs = []; let cur = [];
      for (const q of st.path ?? []) {
        const p = W(q.p), prev = cur[cur.length - 1];
        if (q.landing || (prev && (Math.hypot(p[0] - prev.p[0], p[2] - prev.p[2]) > 1.2 || Math.abs(p[1] - prev.p[1]) > .45))) {
          if (cur.length > 1) runs.push(cur); cur = q.landing ? [] : [{ p, w: q.w }];
        } else cur.push({ p, w: q.w });
      }
      if (cur.length > 1) runs.push(cur);
      for (const run of runs) {
        // (the way across each tread: square to the walk, from its neighbours either side; at either end of the run
        //  the one chord there is turned on by half the turn of the next -- a spiral's last tread faced 12 degrees
        //  off, and its railing post stood beside the newel instead of finding it)
        const ang = (i) => Math.atan2(run[i + 1].p[2] - run[i].p[2], run[i + 1].p[0] - run[i].p[0]);
        const wrap = (t) => Math.atan2(Math.sin(t), Math.cos(t)), last = run.length - 1;
        const n = run.map((q, i) => {
          let t;
          if (i > 0 && i < last) { const a = run[i - 1].p, b = run[i + 1].p; t = Math.atan2(b[2] - a[2], b[0] - a[0]); }
          else if (i === 0) t = last > 1 ? ang(0) - wrap(ang(1) - ang(0)) / 2 : ang(0);
          else t = last > 1 ? ang(last - 1) + wrap(ang(last - 1) - ang(last - 2)) / 2 : ang(last - 1);
          return [-Math.sin(t), Math.cos(t)];
        });
        for (const side of [-1, 1]) {
          // (on the tread's very edge, reaching in at most 17cm: a parapet does not narrow the flight)
          const edge = run.map((q, i) => [q.p[0] + n[i][0] * side * (q.w / 2 - .02), q.p[1], q.p[2] + n[i][1] * side * (q.w / 2 - .02)]);
          // open: no stone beside the tread (at knee and chest height, just past its edge), and a DROP there -- the floor
          // beside more than half a metre below it (where a landing or a doorway is level with it, one steps off, safely)
          const open = run.map((q, i) => openBeside(q.p, [n[i][0] * side, n[i][1] * side], q.w / 2));
          if (open.some((v) => v)) walled[side] = false;
          const inward = (i) => [-n[i][0] * side, -n[i][1] * side];
          // the step's rise, and how far under the nosings the flight's underside is (a solid flight: a stringer's depth)
          const rise = Math.max(.05, (run[run.length - 1].p[1] - run[0].p[1]) / Math.max(1, run.length - 1)), soffit = st.soffit ?? .2;
          // the open stretches: a STRINGER along each (not for stone, which is its own parapet), the posts standing on it,
          // the rail (or the parapet) swept along the posts' tops
          for (let i = 0; i < run.length;) {
            if (!open[i]) { i++; continue; }
            let j = i; while (j + 1 < run.length && open[j + 1]) j++;
            // (a stretch of ONE tread is no railing -- a lone post on the flight's edge, holding no rail, standing on
            //  nothing but the 5 cm of it over the tread: the top tread of a short flight beside a just-too-deep drop)
            if (j === i) { i = j + 1; continue; }
            const pts = edge.slice(i, j + 1), ns = pts.map((_, k) => inward(i + k));
            const off = (p, k, d) => [p[0] - ns[k][0] * d, p[1], p[2] - ns[k][1] * d];   // (d metres out from the edge)
            if (type !== "stone" && pts.length > 1) {
              // THE STRINGER: the board the open side of a flight is closed with -- 6 cm thick, from 1 cm inside the
              // flight's side (buried in it: no face of the two in one plane) to 5 cm outside it; its top a little over the
              // nosings, its foot under the soffit. Swept along the treads' line, half a step on past the first tread (down
              // to the floor it starts from), not past the last (that is the floor it arrives on).
              const a0 = pts[0], a1 = pts[1], foot = [a0[0] - (a1[0] - a0[0]) / 2, a0[1] - (a1[1] - a0[1]) / 2, a0[2] - (a1[2] - a0[2]) / 2];
              const sp = [foot, ...pts].map((p, k) => off(p, Math.max(0, k - 1), .07)), sn = [ns[0], ...ns];
              rail(m, sp, sn, .06, -(rise / 2 + soffit + .03), rise / 2 + .03);
            }
            if (type !== "stone") for (const [k, p] of pts.entries()) {   // (each post on the stringer's middle, from its top into the rail)
              const r = type === "iron" ? .02 : .03, c = off(p, k, .04);
              post(m, c, r - .005, p[1] + rise / 2, p[1] + H - .03);   // (5mm inside the rail's faces: none of its own lies in one)
            }
            if (pts.length > 1) {
              if (type === "stone") rail(m, pts, ns, .15, -.25, H);
              else {   // (the handrail centred over the posts)
                const w = type === "iron" ? .05 : .08;
                rail(m, pts.map((p, k) => off(p, k, .04 + w / 2)), ns, w, H - .06, H + .02);
                if (type === "iron") rail(m, pts.map((p, k) => off(p, k, .055)), ns, .03, H / 2 - .02, H / 2 + .02);
              }
            }
            i = j + 1;
          }
        }
      }
      // ...and round its LANDINGS: along every free edge (no flight arriving or leaving there) wherever it is open -- the
      // flat between two flights of a dog-leg, the platform a flight arrives on -- level, at the same height. The free
      // edges come round the landing in order, so where one ends at a corner the next begins: one railing round it, one
      // post at the corner, the rail mitred there.
      let loop = [];                                     // { p, out, corner }
      const same = (u, v) => Math.abs(u[0] - v[0]) + Math.abs(u[1] - v[1]) + Math.abs(u[2] - v[2]) < 1e-6;
      let prevB = null;
      for (const e of st.edges ?? []) {
        const A = W(e.a), B = W(e.b), o = [e.n[0] * c + e.n[1] * sn, -e.n[0] * sn + e.n[1] * c], ol = Math.hypot(o[0], o[1]) || 1;
        const out2 = [o[0] / ol, o[1] / ol], len = Math.hypot(B[0] - A[0], B[2] - A[2]), k = Math.max(1, Math.ceil(len / .45));
        const pts = Array.from({ length: k + 1 }, (_, q) => ({ p: [A[0] + (B[0] - A[0]) * q / k, A[1], A[2] + (B[2] - A[2]) * q / k], out: out2 }));
        if (prevB && same(prevB, A) && loop.length) {           // (a corner: the two edges' ways out, averaged)
          const last = loop[loop.length - 1], m2 = [last.out[0] + out2[0], last.out[1] + out2[1]], l2 = Math.hypot(...m2) || 1;
          last.out = [m2[0] / l2, m2[1] / l2]; last.corner = true;
          pts.shift();
        } else if (loop.length) loop.push(null);               // (a break: the next stretch stands apart)
        loop.push(...pts);
        prevB = B;
      }
      // (round the whole landing and back to where it began: that corner too is one, and the railing is read from a
      //  break or a closed point, so an open stretch is not cut where the list happens to start)
      const closed = loop.length > 2 && loop[0] && loop[loop.length - 1] && same(loop[0].p, loop[loop.length - 1].p);
      if (closed) {
        const a = loop[0], b = loop.pop(), m2 = [a.out[0] + b.out[0], a.out[1] + b.out[1]], l2 = Math.hypot(...m2) || 1;
        a.out = [m2[0] / l2, m2[1] / l2]; a.corner = true;
      }
      const inset = (q) => [q.p[0] - q.out[0] * .02, q.p[1], q.p[2] - q.out[1] * .02];
      let openAt = loop.map((q) => q && openBeside(inset(q), q.out, .02));
      const cut = openAt.findIndex((v) => !v);
      // (turned to begin there; the list's end meets its start only round a closed landing -- else a break between)
      if (cut > 0) { const gap = closed ? [] : [null]; loop.push(...gap, ...loop.splice(0, cut)); openAt = [...openAt.slice(cut), ...gap, ...openAt.slice(0, cut)]; }
      for (let i = 0; i < loop.length;) {
        if (!loop[i] || !openAt[i]) { i++; continue; }
        let j = i; while (j + 1 < loop.length && loop[j + 1] && openAt[j + 1]) j++;
        const seg = loop.slice(i, j + 1).map(inset), ns = loop.slice(i, j + 1).map((q) => [-q.out[0], -q.out[1]]);
        if (type !== "stone") for (const [q, p] of seg.entries()) {
          const r = type === "iron" ? .02 : .04, cc = [p[0] + ns[q][0] * r, p[1], p[2] + ns[q][1] * r];
          post(ml, cc, r - .005, p[1] - .05, p[1] + H - .03);
        }
        if (seg.length > 1) {
          if (type === "stone") rail(ml, seg, ns, .15, -.25, H);
          else {
            rail(ml, seg, ns, type === "iron" ? .05 : .08, H - .06, H + .02);
            if (type === "iron") rail(ml, seg, ns, .03, H / 2 - .02, H / 2 + .02);
          }
        }
        i = j + 1;
      }
    }
    // A SIDE AGAINST A WALL all the way needs no stringer -- the wall is one -- and its own flat side lay in the wall's
    // face: the two drew over each other wherever the wall showed beside a tread. That side is pushed a centimetre into
    // the wall (the flight's frame: x up the flight, its sides z = 0 on the right and z = -width), out of sight.
    if (st.kind === "flight" && st.path?.length) {
      const w = st.path[0].w, P = st.geometry.position;
      for (const side of [-1, 1]) if (walled[side]) {
        const z0 = side > 0 ? 0 : -w, dz = side > 0 ? .01 : -.01;
        for (let i = 2; i < P.length; i += 3) if (Math.abs(P[i] - z0) < 1e-6) P[i] += dz;
      }
    }
    if (m.counts.tris) out.push({ name: `${st.name} railing`, geometry: m.arrays(), instances: [[0, 0, 0, 0]], kind: "railing", stairPart: st.name });
    if (ml.counts.tris) out.push({ name: `${st.name} landing railing`, geometry: ml.arrays(), instances: [[0, 0, 0, 0]], kind: "railing", stairPart: st.name });
  }
  return out;
}

// `when` on a part: drawn only while a WORD parameter has the value (or one of the values) it names -- a fence's
// `style` picks its rails, pickets, hurdles or dyke; a part without `when` is always drawn
const passes = (when, params) => when === undefined || Object.entries(when).every(([k, v]) => (Array.isArray(v) ? v : [v]).includes(wordOf(k, params)));
// `seat`: A ROOF THAT BEARS ON ITS WALL. A dome or a cone names the wall it stands on (a ring, or an enclosure on a
// `sides` plan) and is lifted -- from its placement's height, as from the ground -- until its SOFFIT meets the wall's
// outer edge 2 cm under the wall head: the rafters on the wall plate, the eaves running on past it, instead of a cone
// guessed at a height that left a hand's breadth of sky over the wall all round (or its foot ring out past the wall in
// the air). The soffit is the dome's inner shell (the outer one for a skin), met where it is LOWEST over the wall: in the
// middle of one of its faces, where its section is nearest the axis.
function seatLift(name, def, defs, params) {
  const P = (v, dd) => num_(v ?? dd, params), w = defs[def.seat];
  if (!w) throw new Error(`"seat": no part named "${def.seat}"`);
  // (a ring's `at` lists its bays: its height is its `place`'s and its `y`)
  const wy = w.type === "ring" ? (w.place ? P(w.place[0][1]) : 0) + P(w.y, 0) : (placements(w, P, params)[0] ?? [0, 0, 0, 0])[2] + P(w.y, 0);
  let edge, top;                                    // (how far the wall's outer face is from the axis, at its nearest; its head)
  if (w.type === "ring") { const n = P(w.count); edge = P(w.rOuter) * (flagOf(w.polygon, params) ? Math.cos(Math.PI / n) : 1); top = wy + P(w.height); }
  else if (w.type === "enclosure" && w.plan?.sides !== undefined) { edge = P(w.plan.radius) * Math.cos(Math.PI / P(w.plan.sides)); top = wy + P(w.height); }
  else throw new Error(`"seat": "${def.seat}" is not a ring or an enclosure on a \`sides\` plan`);
  const d = domeOf(name, def, (v, dd) => num_(v ?? dd, params), params, false), t = P(def.thickness, 0);
  const R0 = d.curve[0][0], H0 = d.rise;
  const soffit = !(t > 0) ? d.curve : d.oculus > 0 ? d.curve.map(([r, y]) => [Math.max(r - t, .02), y])
    : d.curve.map(([r, y]) => [r * Math.max(.05, 1 - t / R0), y * Math.max(.05, 1 - t / H0)]);
  const rho = edge / Math.cos(Math.PI / d.sides);   // (the soffit's own radius over the wall's edge, mid-face)
  let h = null;
  for (let i = 0; i + 1 < soffit.length; i++) {
    const [r0, y0] = soffit[i], [r1, y1] = soffit[i + 1];
    if ((r0 - rho) * (r1 - rho) <= 0 && r0 !== r1) { const y = y0 + (y1 - y0) * (rho - r0) / (r1 - r0); h = h === null ? y : Math.max(h, y); }
  }
  if (h === null) throw new Error(`"seat": its soffit does not reach out over "${def.seat}" (${rho.toFixed(2)} m from the axis)`);
  return top - .02 - h;
}

export function buildPart(name, defs, params) {
  if (defs[name]?.when !== undefined && !passes(defs[name].when, params)) return [];
  const def = defs[name];
  if (def && def.seat && def.type === "dome") {
    const lift = seatLift(name, def, defs, params);
    const out = buildPart(name, { ...defs, [name]: { ...def, seat: undefined } }, params);
    const shift = (q) => ({ ...q, instances: q.instances.map(([a, x, y, z]) => [a, x, y + lift, z]) });
    return Array.isArray(out) ? out.map(shift) : shift(out);
  }
  if (def && def.atop) {
    // `atop`: stand on another part's top -- every placement's height is measured from there
    // (`atopR`: its own radius -- it stands where the dome has narrowed to that; its placement's y then sinks it in)
    const lift = topOf(def.atop, defs, params, def.atopR !== undefined ? num_(def.atopR, params) : 0, def.atopLevel);
    const out = buildPart(name, { ...defs, [name]: { ...def, atop: undefined, atopR: undefined, atopLevel: undefined } }, params);
    const shift = (q) => ({ ...q, instances: q.instances.map(([a, x, y, z]) => [a, x, y + lift, z]) });
    return Array.isArray(out) ? out.map(shift) : shift(out);
  }
  try {
    // `walked: true`: a floor open to the sky that is meant to be walked -- a terrace, a roof walk, a gallery round a
    // drum (the access check asks that it be reached; an open top not so marked is a roof, a cornice, a sill)
    const out = buildPart_(name, defs, params);
    // (both may be expressions over the params, as `glass` may: a component's `terrace` says whether its roof is walked)
    if (flagOf(def?.walked, params)) for (const q of [out].flat()) q.walked = true;
    if (flagOf(def?.flatRoof, params)) for (const q of [out].flat()) q.flatRoof = true;   // (`flatRoof`: a slab that is a roof, not a floor)
    // (`outside`: its faces are the open air's, whatever the finishes' rays make of them -- a dwarf gallery's passage,
    //  open through its arcade but too narrow to look out of: what it is, said where it is designed)
    if (flagOf(def?.outside, params)) for (const q of [out].flat()) q.side = "out";
    // (`light`: built of poles, laths and bark, not masonry -- a longhouse's barrel: it pushes nothing out at its feet)
    if (flagOf(def?.light, params)) for (const q of [out].flat()) q.light = true;
    // (`beam`: the longest lintel its builders could set, metres -- check.js lintels)
    if (def?.beam !== undefined) for (const q of [out].flat()) q.beam = num_(def.beam, params);
    // (`perch`: birds sit on its top as on a roof's ridge -- a merlon; a number is the share of them that has birds)
    if (def?.perch !== undefined && flagOf(def.perch, params)) for (const q of [out].flat()) q.perch = typeof def.perch === "number" ? def.perch : 1;
    return out;
  }
  catch (e) { throw new Error(`part "${name}": ${e.message}`); }   // which part: a bare complaint about a wall is no help in a building of fifty
}
function buildPart_(name, defs, params) {
  const def = defs[name];
  if (!def) throw new Error(`no part named "${name}"`);
  const P = (v, d) => num_(v ?? d, params);
  if (def.oval && ["ring", "vault", "steps", "tunnel"].includes(def.type)) return ovalPart(name, def, defs, params);

  if (def.type === "wall") {
    // (a pattern of openings on a wall of its own `width` is centred in it; without a width, the wall is the pattern's)
    const o = def.openings?.pattern ? patternOpenings(def.openings, params) : null;
    const w = def.width !== undefined && P(def.width) > 0 ? P(def.width) : o ? o.width : 0;   // (0 or none: the pattern's)
    const shift = o ? (w - o.width) / 2 : 0;
    if (shift < -1e-9) throw new Error(`a wall ${w.toFixed(2)}m long cannot hold a pattern ${o.width.toFixed(2)}m long`);
    const openings = glazed(o ? o.openings.map((q) => ({ ...q, at: q.at + shift })) : (def.openings ?? []).map((k) => openingOf(k, P, params)),
                            flagOf(def.glass, params));
    if (def.tiers) {
      // a face in TIERS (build.js tieredWall): bands stacked from the ground, openings measured from its middle
      const g = mesh(), tiers = withLombard(tiersOf(def.tiers, P(def.height), w, P, params).map((t) => ({ ...t, openings: glazed(t.openings, flagOf(def.glass, params)) })), def, params);
      const H = tiers.reduce((a, t) => a + t.h, 0), plan = orderPlan(def, params, H, P(def.thickness), [tiers]);
      const m = tieredWall(mesh(), w, withOrderTops(plan, tiers), (y0) => straightAt(P(def.thickness), def.center === false ? 0 : -w / 2, y0), { glass: g });
      const x0 = def.center === false ? 0 : -w / 2;
      return withCourses(withGlass({ name, geometry: m.arrays(), instances: placements(def, P, params), kind: "wall", bayWidth: w, lintels: lintelsOf([[x0, 0], [x0 + w, 0]], [tiers], P(def.thickness)) }, g),
                         def, params, H, P(def.thickness), [[x0, 0], [x0 + w, 0]], [tiers], false, [], plan);
    }
    const face = Object.assign(wallFace(w, P(def.height), openings), lombardOf(def.lombard, params));
    // WHERE IT STANDS. A round building needs no placement -- a ring IS its placement -- but a straight one is
    // nothing without it: a nave is two arcades a nave's width apart, and its transept is the same wall turned
    // a right angle. `at`: [x, y, z, yaw] per copy, as a column's. `center` measures the wall from its middle
    // rather than its corner, which is how one writes a symmetrical building without arithmetic in every line.
    const map = straightAt(P(def.thickness), def.center === false ? 0 : -w / 2);
    const m = extrude(face, map), x0 = def.center === false ? 0 : -w / 2;
    return withCourses(withGlass({ name, geometry: m.arrays(), instances: placements(def, P, params),
             face, kind: "wall", bayWidth: w, lintels: lintelsOf([[x0, 0], [x0 + w, 0]], [[{ h: P(def.height), openings }]], P(def.thickness)) }, glassPanes(face, map, mesh())),
             def, params, P(def.height), P(def.thickness), [[x0, 0], [x0 + w, 0]], [[{ h: P(def.height), openings }]]);
  }

  if (def.type === "barrel") {
    // A BARREL VAULT, STRAIGHT. The same cross-section the radial `vault` carries round a ring -- an arch's
    // head with the masonry above it, flat on top where the floor or the roof above sits -- carried along a
    // straight line instead: the roof of a nave, an aisle, a porch, a crypt. Its soffit is the arch, its
    // haunches are the solid either side of it, and `top` is its extrados.
    //   As with the ring's vault, `clears` is the height the springing must not fall below (the crown of the
    // arcade it stands on), because a vault that springs too low cuts across the arches it is roofing.
    const width = P(def.width), springing = P(def.springing), top = P(def.top), length = P(def.length);
    if (!(top > springing)) throw new Error(`"${name}": a vault's top must be above its springing line`);
    if (def.clears !== undefined && springing < P(def.clears) - 1e-9) {
      throw new Error(`the vault springs at ${springing.toFixed(2)}m but must clear ${P(def.clears).toFixed(2)}m` +
                      ` -- as it is it would cut across the arches below it`);
    }
    const face = wallFace(width, top - springing, [{
      at: width / 2, width, sill: 0, springing: 0, head: headOf(def.head, params) }]);
    const m = extrude(face, straightAt(length, -width / 2, springing));
    return { name, geometry: m.arrays(), instances: placements(def, P, params),
             face, kind: "barrel" };
  }

  if (def.type === "ring") {                       // a round building's storey: one bay, N times round
    const n = def._n ?? Math.max(3, Math.round(P(def.count)));
    const rOuter = P(def.rOuter), rInner = P(def.rInner);
    // the bay's width AT THE OUTER FACE: the ring closes exactly (`polygon`: the chord between its corners, the faces
    // flat -- build.js chordal)
    const poly = flagOf(def.polygon, params), w = poly ? 2 * rOuter * Math.sin(Math.PI / n) : 2 * Math.PI * rOuter / n;
    // `solid: true` (or no opening at all) is a blind ring: the cavea's substructure is a mass of masonry with
    // the podium wall as its inner face, not an arcade.
    const opening = def.opening ?? {};
    const openings = (def.solid || def.opening === null) ? [] : [
      { ...openingOf({ ...opening, width: opening.width ?? w * .55, at: 0 }, P, params), at: w / 2 }].map((o) => glazed([o], flagOf(def.glass, params))[0]);
    // (`lombard`: the band and its arches round the ring under its top, bay by bay -- a lesene at each end of every bay,
    //  meeting the next bay's: `lesene` is each half's width -- lombard.js)
    const face = Object.assign(wallFace(w, P(def.height), openings), lombardOf(def.lombard, params));
    const rmap = poly ? chordal(rOuter, rInner, n, w) : radial(rOuter, rInner, w), m = extrude(face, rmap);
    // [y-rotation, x, y, z] per instance: the bay is built in its own wedge, so the ring is rotations of it
    const t = turnOf(def, n, P);
    // `place` puts the whole ring somewhere (a cathedral's three tribunes stand on three sides of its octagon,
    // not at the origin); without it a ring is its own placement, at the middle of the world. It is NOT `at`:
    // on a ring that already names which BAYS are the part's own.
    // ...and `repeat` stacks it, as it does a straight part: the storeys of a round tower
    const seats = placements({ place: def.place ?? [[0, 0, 0, 0]], repeat: def.repeat }, P, params);
    const instances = seats.flatMap(([yaw, x, y, z]) => baysFor({ ...def, _name: name }, n, P)
      .map((k) => [k * 2 * Math.PI / n + t + yaw, x, y + P(def.y, 0), z]));
    // (its COURSES along the bay's own outer polygon -- its corners and its jambs, the points the face is drawn
    //  through -- mitred into the next bays round, which are the same bay turned: they come as ghost segments. A ring
    //  of some of the bays has its others in a sibling part -- the bay with the door -- whose courses take up there)
    const ring = withGlass({ name, geometry: m.arrays(), instances, face, kind: "ring", bayWidth: w, count: n }, glassPanes(face, rmap, mesh()));
    const spec = coursesSpec(def.courses, params);
    // ...and its ORDER (order.js), the ring's height: a pilaster on every pier, folded over the corner between two bays
    // (each bay draws a half at either end of its face: the next bay, the same bay turned, draws the other), the
    // entablature round as a course -- the Colosseum's storeys, a rotunda's
    const H = P(def.height), ords = (def.orders ?? []).filter((o) => wordOf(o.kind ?? "tuscan", params) !== "none").map((o) => ({ kind: wordOf(o.kind ?? "tuscan", params), y0: 0, y1: H,
      ends: o.ends === undefined ? true : flagOf(o.ends, params), ...(o.proj !== undefined ? { proj: num_(o.proj, params) } : {}) }));
    if (!spec && !ords.length) return ring;
    // (`dress: "in"`: on its INNER face -- the court side of a gallery's inner wall, a cavea's podium -- walked the other
    //  way round, so that what it faces is on the left as on the outer face; `u` along the walk, the face's x backwards)
    const inner = wordOf(def.dress, params) === "in", fx = (u) => (inner ? w - u : u), sg = inner ? -1 : 1;
    const ows = face.openings.map((o) => ({ ...o, x0: inner ? w - o.x1 : o.x0, x1: inner ? w - o.x0 : o.x1 }));
    const xs = [...new Set([0, ...ows.flatMap((o) => [o.x0, o.x1]), w].map((x) => +x.toFixed(9)))].sort((a, b) => a - b);
    const at = (u) => { const [X, , Z] = rmap(fx(u), 0, inner ? 1 : 0); return [X, Z]; }, pts = xs.map(at);
    const full = true, turn = (q, a) => [q[0] * Math.cos(a) + q[1] * Math.sin(a), -q[0] * Math.sin(a) + q[1] * Math.cos(a)];
    const line = full ? [turn(at(xs[xs.length - 2]), -sg * 2 * Math.PI / n), ...pts, turn(at(xs[1]), sg * 2 * Math.PI / n)] : pts, o0 = full ? 1 : 0;
    const gaps = line.slice(1).map((_, i) => {
      const k = i - o0, a = xs[k], b = xs[k + 1];
      if (k < 0 || k + 1 >= xs.length) return [];
      const L = Math.hypot(...[0, 1].map((j) => line[i + 1][j] - line[i][j]));
      return ows.filter((o) => o.x0 < b - 1e-9 && o.x1 > a + 1e-9).map((o) => ({ x0: 0, x1: L, y0: o.sill, y1: o.crown }));
    });
    const courses = spec || ords.length ? coursesOf(ords.length ? { ...(spec === true || !spec ? {} : spec), cornice: false } : spec, H, rOuter - rInner, []) : [];
    const sized = ords.map((o) => {
      const under = courses.filter((c) => c.y <= 1e-6 && c.y + c.h > 0).sort((a, b) => b.y + b.h - a.y - a.h)[0];
      const foot = under ? under.y + under.h : 0, os = orderSize(o.kind, ORDERS[o.kind], H - foot, o);
      courses.push({ y: foot + os.col, h: os.ent, out: Math.max(...os.profile.map(([q]) => q)), pts: os.profile });
      return { ...o, foot, yb: under ? under.y : foot, s: os };
    });
    const cm = coursesMesh(mesh(), line, courses, { gaps, ghost: new Set(full ? [0, line.length - 2] : []) });
    // (the pilasters on the bay's face from its first corner to its last: the chord between them -- a polygon's face, or
    //  near enough a round ring's over a pier's width -- each corner turning by the bay's own angle: in, on the inner face)
    const A = at(0), B = at(w), L = Math.hypot(B[0] - A[0], B[1] - A[1]), e = [(B[0] - A[0]) / L, (B[1] - A[1]) / L], k = sg * Math.tan(Math.PI / n);
    for (const o of sized) {
      const ops = ows.filter((q) => q.sill < o.foot + o.s.col && q.crown > o.foot).map((q) => ({ x0: q.x0 * L / w, x1: q.x1 * L / w }));
      const { spots, folds } = pilasterSpots(L, ops, o.s, { ends: o.ends ? ["fold", "fold"] : false });
      for (const x of spots) pilasterMesh(cm, A, e, [-e[1], e[0]], x, o.foot, o.s, 0, 0, o.yb);
      for (const x of folds) pilasterMesh(cm, A, e, [-e[1], e[0]], x, o.foot, o.s, x > 0 ? -1 : 1, k, o.yb);
    }
    return cm.counts.tris ? [...[ring].flat(), { name: name + " courses", geometry: cm.arrays(), instances, kind: "moulding", shell: true }] : ring;
  }

  if (def.type === "vault") {
    // A ring of barrel vaults over the corridor between two walls -- what an arena's ambulatory is roofed
    // with. One bay's wedge is the vault's cross-section swept between its two radial planes, and the
    // cross-section is a wall face whose single opening spans the whole width: the solid left over is the
    // vault's own masonry, and the void under it is the corridor. Its extrados is flat at `top`, which is the
    // floor of the storey above.
    const n = def._n ?? Math.max(3, Math.round(P(def.count)));
    const rIn = P(def.rInner), rOut = P(def.rOuter), springing = P(def.springing);
    const top = P(def.top), width = rOut - rIn;
    if (width <= 0) throw new Error("a vault's outer radius must be beyond its inner one");
    // A VAULT SPRINGS FROM ABOVE WHAT IT ROOFS. Its soffit is lowest where it meets the wall, so a vault that
    // springs at the arcade's own springing line hangs across the top of every arch it is supposed to cover.
    // `clears` is the height it must start at or above -- the crown of the arches below -- and the engine
    // refuses rather than quietly building something that blocks its own openings.
    if (def.clears !== undefined && springing < P(def.clears) - 1e-9) {
      throw new Error(`the vault springs at ${springing.toFixed(2)}m but must clear ${P(def.clears).toFixed(2)}m` +
                      ` -- as it is it would cut across the arches below it`);
    }
    const face = wallFace(width, top - springing, [{
      at: width / 2, width, sill: 0, springing: 0, head: headOf(def.head, params) }]);
    const m = extrude(face, sweep(rIn, Math.PI / n, springing));
    const t = turnOf(def, n, P);
    // (`place`, as a ring's: an apse's ambulatory is vaulted round the apse's centre, not the world's)
    const seats = placements({ place: def.place ?? [[0, 0, 0, 0]] }, P, params);
    const instances = seats.flatMap(([yaw, x, y, z]) => baysFor({ ...def, _name: name }, n, P)
      .map((k) => [k * 2 * Math.PI / n + t + yaw, x, y + P(def.y, 0), z]));
    return { name, geometry: m.arrays(), instances, face, kind: "vault", count: n,
             bayWidth: 2 * Math.PI * rOut / n };
  }

  if (def.type === "steps") {
    // Seating, or a flight of stairs -- the same part at different scales. It is a stepped cross-section swept
    // through a bay's wedge, standing on `base` (the vaults' flat extrados) and rising outward with the cavea.
    // `every`/`offset` say which bays get it: leave every fifth bay out and those gaps are the vomitoria, with
    // a narrower, finer-stepped flight of the same part climbing in them.
    const n = def._n ?? Math.max(3, Math.round(P(def.count)));
    const rIn = P(def.rInner), rOut = P(def.rOuter), run = P(def.run);
    const base = P(def.base, 0);
    // How many steps: for a flight that runs radially, as many as fit between the two radii; for one that
    // climbs ALONG the ring the radii are its corridor, not its length, so the rise says how many there are.
    const cols = Math.max(1, (def.plan === "along")
      ? Math.round(def.steps !== undefined ? P(def.steps) : (P(def.top) - base) / P(def.rise))
      : Math.floor((rOut - rIn) / run + 1e-3));   // (radii and run rounded to the tenth of a millimetre: twenty runs can
                                                  //  come out a hair over the depth, and the floor drop the last row)
    // `top` says where the flight must ARRIVE and the rise follows from it -- which is how a stair that has to
    // meet a given row of seating is written, rather than by guessing a rise and finding it lands short.
    // `first` raises the first tread on its own: a mass standing on a tunnel head whose top must continue the
    // seating outside it starts at the height that seating has already reached, not one riser above its base.
    const first = def.first !== undefined ? P(def.first) : undefined;
    const rise = def.top !== undefined
      ? (P(def.top) - base - (first ?? 0)) / (first !== undefined ? cols - 1 : cols)
      : P(def.rise);
    const span = Math.max(.02, Math.min(1, P(def.span, 1)));
    // A STAIR IS FOR FEET. Say `use: "stair"` and the part holds itself to what a person can climb: a rise
    // between 12 and 22cm on a tread of at least 25cm (a Roman vomitorium is steep, not impossible). Seating
    // is not a stair -- a row is a 45cm rise on a 70cm tread -- so the check is asked for, not assumed.
    if (def.use === "stair" && (rise < .12 || rise > .22 || run < .25)) {
      throw new Error(`"${name}" is declared a stair but its steps are ${(rise * 100).toFixed(1)}cm on a ` +
                      `${(run * 100).toFixed(1)}cm tread -- a climbable flight is 12-22cm on 25cm or more`);
    }
    // WHICH SURFACES. No `faces` means a solid. Otherwise: "top" the treads and risers, "base" the flat
    // underside (a tunnel's soffit, seen from inside it), "ends" the verticals at either end, "sides" the two
    // faces of the sweep -- which for a wedge are its radial planes, and for a passage are its side walls.
    const faces = def.faces ? [].concat(def.faces) : null;
    const both = faces && (faces.includes("sides") ||
                          (faces.includes("side-in") && faces.includes("side-out")));
    const emit = faces && {
      caps: both ? true : faces.includes("side-out") ? "front" : faces.includes("side-in") ? "back" : false,
      walls: faces.filter((f) => !f.startsWith("side"))
                  .flatMap((f) => f === "ends" ? ["end-in", "end-out"] : [f]) };
    // (`soffit: [yIn, yOut]`: heights of its underside at rInner and rOuter, absolute as `base` is -- build.js stepsFace)
    // (`landing`: the last tread carried on out past rOuter -- a walkway behind the top row, and the mass under it)
    const stepOpts = { base: 0, rising: def.rising ?? "out", landing: P(def.landing, 0), strips: def.plan === "along", ...(first !== undefined ? { first } : {}), ...(def.soffit ? { soffit: [P(def.soffit[0]) - base, P(def.soffit[1]) - base] } : {}) };
    const face = stepsFace(cols, run, rise, stepOpts);
    const half = span * Math.PI / n, centre = P(def.spanOffset, 0) * Math.PI / n;
    const t = turnOf(def, n, P);
    const instances = baysFor({ ...def, _name: name }, n, P).map((k) => [k * 2 * Math.PI / n + t, 0, 0, 0]);
    // HOW THE CROSS-SECTION IS CARRIED ROUND. `wedge` sweeps it between the bay's radial planes (seating);
    // `parallel` runs it out along one ray with fixed-width sides (a passage, which must not fan out to half
    // again its width at the facade); `flank` is the seating beside such a passage, bay plane on one side and
    // passage wall on the other; `along` climbs round the ring instead of across it (the stair between levels).
    const plan = def.plan ?? "wedge";
    const halfW = P(def.width, 0) / 2, halfBay = Math.PI / n;
    const mapFor = (sign) => plan === "parallel" ? corridor(rIn, halfW, base, centre)
                           : plan === "flank" ? flank(rIn, halfBay, halfW, base, sign)
                           : plan === "along" ? along(rIn, rOut, P(def.rArc, (rIn + rOut) / 2), base,
                                                      -cols * run / (2 * P(def.rArc, (rIn + rOut) / 2)))
                           : sweep(rIn, half, base, sign * centre);
    const topOf = base + (first ?? rise) + (cols - 1) * rise;
    const parts = [{ name, geometry: extrude(face, mapFor(1), mesh(), emit).arrays(), instances, face,
                     kind: "steps", count: n, rows: cols, topOf, shell: !!emit }];
    // A STAIR'S WALKING LINE (`use: "stair"`): every tread's middle and its width, bottom first, as a flight carries
    // one -- so the walk ramps it (its risers are steps, not walls: three of them within a stride are a wall's height
    // in the wall field, and the climb stopped there), the railings look along its sides and the stair check asks
    // for headroom over it
    if (def.use === "stair") {
      const m = mapFor(1), out = stepOpts.rising === "out", f0 = first ?? rise;
      parts[0].path = Array.from({ length: cols }, (_, j) => {
        const c = out ? j : cols - 1 - j, y = out ? f0 + c * rise : (cols - c) * rise;
        const a = m((c + .5) * run, y, 0), b = m((c + .5) * run, y, 1);
        return { p: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2], w: Math.hypot(a[0] - b[0], a[2] - b[2]) };
      });
      // (and where it is stepped onto: half a metre before its first tread, on its base -- as a flight's foot)
      const fx = out ? -.5 : cols * run + .5, a = m(fx, 0, 0), b = m(fx, 0, 1);
      parts[0].foot = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2];
    }
    // a mirrored pair: the same piece either side of the passage, which is the seating that flanks a slot
    if (def.mirror) {
      const f2 = stepsFace(cols, run, rise, stepOpts);
      parts.push({ name: name + " (mirrored)", instances, kind: "steps", count: n, rows: cols, topOf,
                   shell: !!emit, geometry: extrude(f2, mapFor(-1), mesh(), emit).arrays() });
    }
    return parts.length === 1 ? parts[0] : parts;
  }

  if (def.type === "tunnel") {
    // The void a passage runs in, as its surfaces: `floor` and `ceiling` are each [height at rInner, height at
    // rOuter], so a stair's tunnel has its ceiling on the flight's slope and a landing's or a level passage's is
    // flat. `faces` as for steps: "top" the ceiling, "sides" the two walls between floor line and ceiling line,
    // "base" the floor, "end-in"/"end-out" the ends. It is laid out like a parallel passage (`width`) and takes
    // the same bay selection.
    const n = def._n ?? Math.max(3, Math.round(P(def.count)));
    const rIn = P(def.rInner), rOut = P(def.rOuter), pair = (v) => [P(v[0]), P(v[1])];
    const [f0, f1] = pair(def.floor), [c0, c1] = pair(def.ceiling);
    if (!(rOut > rIn) || c0 <= f0 || c1 <= f1) throw new Error(`"${name}": a tunnel needs rOuter > rInner and its ceiling above its floor at both ends`);
    const faces = [].concat(def.faces ?? ["top", "sides"]);
    const emit = { caps: faces.includes("sides") ? true : false,
                   walls: faces.filter((f) => f !== "sides").flatMap((f) => f === "ends" ? ["end-in", "end-out"] : [f]) };
    const t = turnOf(def, n, P);
    const instances = baysFor({ ...def, _name: name }, n, P).map((k) => [k * 2 * Math.PI / n + t, 0, 0, 0]);
    const face = tunnelFace(rOut - rIn, f0, f1, c0, c1);
    return { name, geometry: extrude(face, corridor(rIn, P(def.width) / 2, 0, 0), mesh(), emit).arrays(), instances, face,
             kind: "tunnel", count: n, shell: true };
  }

  if (def.type === "groin") {
    // ONE BAY of a groin vault: two barrels crossing, meeting each wall along that wall's own arch. `across`
    // and `along` are the two heads (a rectangular bay's are different arches); `top` is the extrados.
    const { width, length, springing, curveX, curveZ } = groinOf(def, P, params), top = P(def.top);
    const crown = springing + Math.max(...curveX.map(([, y]) => y), ...curveZ.map(([, y]) => y));
    if (top < crown - 1e-6) throw new Error(`its extrados is at ${top.toFixed(2)}m but its crown reaches ${crown.toFixed(2)}m`);
    if (def.clears !== undefined && springing < P(def.clears) - 1e-9) {
      throw new Error(`the vault springs at ${springing.toFixed(2)}m but must clear ${P(def.clears).toFixed(2)}m`);
    }
    // four webs, one per wall, each carrying its wall's own arch in to the groins (build.js groinVault)
    const m = groinVault(mesh(), { width, length, curveX, curveZ, springing, top });
    return { name, geometry: m.arrays(), instances: placements(def, P, params),
             kind: "groin", crown };
  }

  if (def.type === "dome") {
    // A DOME: an arch profile turned about its axis. Whatever an arch can be, a dome can be -- `semicircular`
    // the hemisphere, `segmental` the lowered (saucer) dome, `pointed` the Gothic and Florence's quinto acuto,
    // `horseshoe` the Moorish one that swells past its drum, `onion` the bulb, `trigonal` a cone, `inflexed` a
    // flared spire. The horizontal section is a regular polygon of `sides`: a NUMBER when the dome is built of
    // webs (Florence's eight), and left out when it is ROUND -- then it follows the detail level like every
    // other curve, four quarters of `per90` points. `oculus` is the opening at the crown the lantern stands on;
    // `thickness` 0 makes it a skin (a roof over a tower) rather than two shells of masonry; `sweep` .5 is a
    // SEMIDOME, the half over an apse, closed along its cut and open toward -z. It has no ribs:
    // those are laid on it by a `ribs` part.
    const { m, instances, rise, sweep: share, curve } = domeOf(name, def, P, params);
    // a masonry PART of a dome -- an apse's half vault, an iwan's hood, an exedra's conch -- is a VAULT, the stone of
    // the vault it continues; a whole dome, or a skin, is a dome (and a roof's colour)
    const kind = share < 1 && P(def.thickness, 0) > 0 ? "vault" : "dome";
    // (a part-dome's open face, its cut, for the check: the meridian's right half, in the plane z = 0)
    return { name, geometry: m.arrays(), instances, kind, rise, shell: def.cap === false,
             // (the cut a SEMIDOME's open side stands in -- not the jambs of a doorway cut out of a whole one's foot)
             ...(share <= .5 + 1e-9 ? { cut: curve.filter(([x]) => x >= -1e-9) } : {}) };
  }

  if (def.type === "ribs") {
    // RIBS LAID ON what they stand on -- `on` names the part, and the ribs are set out from ITS numbers, so they
    // cannot disagree with it. On a DOME: `count` of them (the dome's sides unless said) up its meridians, on
    // its groins unless `turn`ed, `width` across and `depth` standing proud of its back. On a GROIN VAULT: the
    // Gothic rib vault -- the two diagonals along its groins, `width` across and hanging `depth` below them,
    // and with `wall: { width, depth }` the arches round its sides as well.
    const on = defs[def.on];
    if (on && on.type === "groin") {
      const g = groinOf(on, P, params);
      const m = groinRibs(mesh(), { ...g, rib: { width: P(def.width), depth: P(def.depth) },
                                    wallRib: def.wall ? { width: P(def.wall.width), depth: P(def.wall.depth) } : null });
      return { name, geometry: m.arrays(), instances: placements(on, P, params), kind: "ribs" };
    }
    if (!on || on.type !== "dome") throw new Error(`ribs must be laid "on" a dome or a groin vault, and "${def.on}" is neither`);
    const d = domeOf(def.on, on, P, params, false);
    const m = domeRibs(mesh(), { sides: d.sides, sweep: d.sweep, domeTurn: d.turn, curve: d.curve, oculus: d.oculus, count: Math.round(P(def.count, d.sides)),
                                 turn: P(def.turn, 0), width: P(def.width), depth: P(def.depth) });
    return { name, geometry: m.arrays(), instances: d.instances, kind: "ribs" };
  }

  if (def.type === "pendentives") {
    // PENDENTIVES (build.js pendentives): the four spherical triangles that carry a round dome on four arches
    // over a square `span` wide, springing where the arches do; the dome on them is `span`/2 inside at its
    // springing, `springing + span/2` up, with `turn: -0.5` and the same `sides`. `sail: true` is the whole
    // sphere instead: the sail vault over a square bay.
    const span = P(def.span), n = Math.round(def.sides !== undefined ? P(def.sides) : 4 * detailOf(params));
    const m = pendentives(mesh(), { span, springing: P(def.springing, 0), sides: n, rows: Math.round(P(def.rows, Math.max(2, detailOf(params) / 2))),
                                    sail: !!def.sail });
    const part = { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "pendentives", shell: true,
                   crown: P(def.springing, 0) + span / 2 };
    if (!def.deck) return part;
    // `deck: { thickness, out }`: the flat roof over the square's four corners at the crown, cut round the drum's
    // circle (the dome's own polygon: a corner every 2pi/sides from the axis) and reaching `out` past the square into
    // the walls -- what the drum rises through, and what the roof walk round a drum is
    // (a quarter per corner, each its own solid: two quarters meet face to face on the axes)
    const r = span / 2, h = r + P(def.deck.out, .4), th = P(def.deck.thickness, .4), q = Math.max(1, Math.round(n / 4));
    const quarters = [[1, 1], [-1, 1], [-1, -1], [1, -1]].map(([sx, sz], i) => {
      const arc = Array.from({ length: q + 1 }, (_, k) => { const a = k * Math.PI / 2 / q; return [sx * r * Math.sin(a), sz * r * Math.cos(a)]; });
      const dm = prismMesh(mesh(), planPoints({ points: [[sx * h, sz * h], [0, sz * h], ...arc, [sx * h, 0]] }), part.crown, part.crown + th);
      return { name: `${name} deck ${i + 1}`, geometry: dm.arrays(), instances: part.instances, kind: "prism" };
    });
    return [part, ...quarters];
  }

  if (def.type === "crepidoma") {
    // THE STEPPED PLATFORM a Greek temple stands on: `steps` steps of `stepH`, each `stepOut` wider all round
    // than the one above, the top one -- the stylobate -- `width` by `length`. One solid, stepped (build.js
    // roofMesh: a stack of rectangles), not boxes piled on each other.
    // `batter`: each step's face leans in by that much from its foot to its top (a Maya pyramid's talud terraces)
    // `tablero`: the share of each step's height that stands VERTICAL over the leaning talud -- Mesoamerica's talud-tablero,
    // the panel band a terrace's frieze is cut in (its panels are a skin laid on it, by the building)
    const W = P(def.width) / 2, L = P(def.length) / 2, n = Math.round(P(def.steps, 3)), h = P(def.stepH, .3), o = P(def.stepOut, .35), bt = P(def.batter, 0);
    const tb = Math.max(0, Math.min(.9, P(def.tablero, 0)));
    const levels = [];
    for (let i = 0; i < n; i++) {
      const e = o * (n - 1 - i), at = (d, y) => ({ x0: -W - e - d, x1: W + e + d, z0: -L - e - d, z1: L + e + d, y });
      levels.push(at(bt, i * h), at(0, (i + 1 - tb) * h));
      if (tb > 0) levels.push(at(0, (i + 1) * h));
    }
    return { name, geometry: roofMesh(mesh(), levels).arrays(), instances: placements(def, P, params), kind: "crepidoma", top: n * h };
  }

  if (def.type === "roof") {
    // A ROOF: `form` (gable, hip, mansard, ... see build.js roofLevels) over a `width` x `length` plan, the
    // ridge along the length, `y` 0 where it meets the wall plane and `overhang` carrying the eave out past it.
    const a = P(def.width) / 2, b = P(def.length) / 2;
    const opt = { a, b };
    for (const k of ["pitch", "thickness", "lowerPitch", "breakH", "clip", "hipH", "ridge"]) if (def[k] !== undefined) opt[k] = P(def[k]);
    // (`chamfer`: over a chamfered plan -- the corners cut that far along each side, in the wall plane: build.js
    //  chamferLevels)
    const lv0 = roofLevels(wordOf(def.form ?? "gable", params), opt), ch = def.chamfer !== undefined ? P(def.chamfer) : 0;
    const cham = (lv) => (ch > 0 ? chamferLevels(lv, lv0, ch) : lv);
    const levels = cham(overhang(lv0, P(def.overhang, 0)));
    // `shell`: a covering that thick over an open roof space (a loft, an attic) instead of a roof solid down to its eaves --
    // the underside follows the slopes, the gables stand in the wall plane (build.js roofMesh)
    const inner = def.shell !== undefined ? cham(overhang(lv0, P(def.overhang, 0), false)).map((L) => ({ ...L, y: L.y - P(def.shell) })) : null;
    // A CHINESE ROOF (build.js curvedRoof) when it says how its slopes bend (`lo`, `hi`: the jujia slopes at the eave
    // and at the ridge, as a profile's) or that its corners turn up (`upturn`, `flare`, over `reach` metres)
    const chinese = ["lo", "hi", "upturn", "flare"].some((k) => def[k] !== undefined);
    const m = chinese ? curvedRoof(mesh(), levels, { lo: P(def.lo, .35), hi: P(def.hi, 1.2), steps: Math.round(P(def.steps, 2 * detailOf(params) + 2)),
                                                     upturn: P(def.upturn, 0), flare: P(def.flare, 0), reach: def.reach !== undefined ? P(def.reach) : undefined,
                                                     perSide: Math.round(P(def.perSide, Math.max(4, 2 * detailOf(params)))) })
                      : roofMesh(mesh(), levels, inner, wordOf(def.open, params) ?? null);
    const roof = { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "roof", ridge: levels[levels.length - 1].y };
    // (`frieze`: a gable's rising arched frieze up its rakes -- lombard.js -- a moulding of its own)
    if (!def.frieze || chinese) return roof;
    const fz = def.frieze === true ? {} : Object.fromEntries(Object.entries(def.frieze).filter(([k]) => !k.startsWith("_"))
      .map(([k, v]) => [k, k === "ends" ? v.map((e) => P(e)) : P(v)]));
    return [roof, { name: name + " frieze", geometry: gableFriezeMesh(mesh(), levels, fz).arrays(), instances: roof.instances, kind: "moulding", shell: true }];
  }

  if (def.type === "flight") {
    // A STRAIGHT FLIGHT of stairs: the same stepped cross-section the ring's `steps` sweeps round a bay,
    // carried along a line. `width` is the flight's, `rise`/`run` a step's, and `top` says where it must
    // arrive (the rise follows from it, as for the ring's). It is checked like one: a climbable flight is a
    // 12-22cm rise on a tread of 25cm or more.
    const run = P(def.run), width = P(def.width), base = P(def.base, 0);
    const steps = Math.max(1, Math.round(def.steps !== undefined ? P(def.steps) : (P(def.top) - base) / P(def.rise)));
    const rise = def.top !== undefined ? (P(def.top) - base) / steps : P(def.rise);
    // (`steep`: a stair of another age -- a Maya pyramid's, a tower's ladder-like flight -- may climb 30cm on 22cm)
    const [maxRise, minRun] = def.steep ? [.30, .22] : [.22, .25];
    if (def.use !== "ramp" && (rise < .12 || rise > maxRise || run < minRun)) {
      throw new Error(`its steps are ${(rise * 100).toFixed(1)}cm on a ${(run * 100).toFixed(1)}cm tread` +
                      ` -- a climbable flight is 12-${maxRise * 100}cm on ${minRun * 100}cm or more` + (def.steep ? "" : " (`steep` for a steeper, older kind)"));
    }
    // IT ARRIVES ON A LANDING: its last tread is `landing` metres longer -- the platform at the top, the same solid
    // (a flight never ends on its last tread; `landing: 0` for one that arrives on a floor of its own)
    const landing = (def.rising ?? "out") === "out" ? P(def.landing, Math.max(1.2, width)) : 0;
    // `soffit`: an OPEN stair -- its underside a sloping soffit that far under the nosings (build.js flightFace, as a
    // spiral's), room beneath it: a cellar's flight under the house's stair. Without it the flight is solid to its base.
    const soff = def.soffit !== undefined ? P(def.soffit) : null;
    const face = soff !== null ? flightFace(steps, run, rise, soff, 0, true) : stepsFace(steps, run, rise, { base: 0, rising: def.rising ?? "out", landing });
    const m = extrude(face, straightAt(width, 0, base));
    if (soff !== null && landing > 0) extrude(slabFace(steps * run, steps * run + landing, steps * rise, soff), straightAt(width, 0, base), m);
    const top = base + steps * rise, L = steps * run;
    const path = [];
    for (let k = 0; k < steps; k++) path.push({ p: [(k + .5) * run, base + (k + 1) * rise, -width / 2], w: width });
    if (landing > 0) path.push({ p: [L + landing / 2, top, -width / 2], w: width, landing: true });
    // (its landing's three free edges -- ahead and either side -- where a railing may run: railingsFor)
    const edges = landing > 0 ? [{ a: [L, top, 0], b: [L + landing, top, 0], n: [0, 1] }, { a: [L + landing, top, 0], b: [L + landing, top, -width], n: [1, 0] },
                                 { a: [L + landing, top, -width], b: [L, top, -width], n: [0, -1] }] : [];
    // (`walk: false`: stepped stone that is not a way up -- a balustrade, a stepped coping -- has no walk to check)
    // (its APPROACH: the floor before its first riser, as deep as the flight is wide (2m for a broader one), where one
    //  stands to begin the climb -- check.js asks it to be floor, and clear)
    const fl = { name, geometry: m.arrays(), instances: placements(def, P, params),
             face, kind: "flight", steps, rise, run, soffit: soff, topOf: top, ...(def.walk === false ? {} : { path, edges, foot: [-.5, base, -width / 2], approach: { x0: -Math.min(width, 2), x1: 0, z0: -width, z1: 0, y: base } }) };
    // (`arrive`: the floor it arrives on, built under it -- arrivalFloor)
    return def.arrive ? [fl, ...arrivalFloor(name, def, P, params, { tops: [{ a: [L + landing, top, 0], b: [L + landing, top, -width], out: [1, 0] }], soffit: soff ?? .3 })] : fl;
  }

  if (def.type === "spiral-stair") {
    // A SPIRAL STAIR: one flight with its own soffit (build.js flightFace) wound round a newel. `radius` is the
    // outside of the treads, `newel` the post they turn round, `turn` the degrees each step turns; `top` says
    // where it arrives and the rise follows from it (or `rise` and `steps`). Its tread is measured on the
    // WALKING LINE halfway out, where a foot actually lands. `hand` "left" winds it the other way; `post`
    // false leaves the newel out (an open well: the treads then show their inner ends).
    //   `follow: { head, radius, inset, width }` winds it round a CURVE instead -- a dome's meridian struck with
    // that head over that radius: at every step's height the stair's outer edge is `inset` inside the curve and
    // its inner edge `width` further in. A stair between a dome's two shells climbs this way.
    //   It ARRIVES on a landing, `landing` metres of level slab continuing the turn (a stair never ends on its
    // last tread; `landing: 0` for one that arrives on a floor of its own).
    const hand = wordOf(def.hand ?? "right", params) === "left" ? -1 : 1;   // (a word, or a param holding one: a component's `hand`)
    const soffit = P(def.soffit, .25);
    let near, far, run, n, rise, post = def.post !== false, r0 = 0, R = 0, turn = 0, rArc = 0;
    if (def.follow) {
      const F = def.follow, rows = domeRows(domeCurve(P(F.radius), F.head, params), 0, 0);
      const radiusAt = (y) => {                       // the curve's radius at height y over its springing
        for (let i = 0; i + 1 < rows.length; i++) if (y >= rows[i][1] - 1e-9 && y <= rows[i + 1][1] + 1e-9) {
          const f = (y - rows[i][1]) / Math.max(1e-9, rows[i + 1][1] - rows[i][1]);
          return rows[i][0] + (rows[i + 1][0] - rows[i][0]) * f;
        }
        return rows[rows.length - 1][0];
      };
      run = P(def.run, .3); rise = P(def.rise, .19);
      n = Math.max(1, Math.round(P(def.top) / rise)); rise = P(def.top) / n;
      // `insetTop`: the inset at the top, grown from `inset` at the foot -- the gap between two shells is not the same
      // all the way up, and a stair close under the outer one at the foot must draw away from it as it curves in
      const inset = P(F.inset, 1), insetTop = P(F.insetTop, P(F.inset, 1)), width = P(F.width, 1.2), slope = rise / run, T = P(def.top);
      far = (x) => { const y = Math.max(0, Math.min(T, x * slope)); return radiusAt(y) - (inset + (insetTop - inset) * y / T); };
      near = (x) => far(x) - width;
      post = false;
      if (near(n * run) < .5) throw new Error("the curve it follows closes in before the stair reaches its top");
    } else {
      R = P(def.radius); r0 = P(def.newel, R * .15); turn = P(def.turn, 30) * Math.PI / 180;
      rArc = (R + r0) / 2; run = rArc * turn;
      n = Math.max(1, Math.round(def.steps !== undefined ? P(def.steps) : P(def.top) / P(def.rise, .19)));
      rise = def.top !== undefined ? P(def.top) / n : P(def.rise);
      const perTurn = 2 * Math.PI / turn, head = perTurn * rise - soffit - rise;
      if (n * turn > 2 * Math.PI && head < 1.9) {
        throw new Error(`a full turn above a tread there is only ${head.toFixed(2)}m of headroom -- turn less per step or rise more`);
      }
      near = () => r0; far = () => R;
    }
    if (rise < .12 || rise > .22 || run < .2) {
      throw new Error(`its steps are ${(rise * 100).toFixed(1)}cm on ${(run * 100).toFixed(1)}cm at the walking line` +
                      ` -- a spiral is climbable at 12-22cm on 20cm or more (widen it, or turn less per step)`);
    }
    // (a follow of `sides` bends round the polygon its dome is: the dome's corners at (k + .5) of its sides, the
    //  stair's own turn -- its placement's yaw -- taken off so the two agree)
    const poly = def.follow?.sides ? { n: Math.round(P(def.follow.sides)), phase: (placements(def, P, params)[0]?.[0] ?? 0) } : null;
    const map = def.follow ? helixAlong(near, far, hand, .25, poly) : helix(r0, R, rArc, hand);
    const top = n * rise, landing = P(def.landing, Math.max(1.2, far(n * run) - near(n * run)));
    const face = flightFace(n, run, rise, soffit, 0);
    // with a post, the treads' inner ends are inside it and are not drawn
    const capsKeep = post ? (hand > 0 ? "front" : "back") : true;
    const m = extrude(face, map, mesh(), { caps: capsKeep, walls: ["top", "base", "joint-in", ...(landing > 0 ? [] : ["joint-out"])] });
    if (landing > 0) extrude(slabFace(n * run, n * run + landing, top, soffit), map, m, { caps: capsKeep, walls: ["top", "base", "joint-out"] });
    // the WALKING PATH, for the clearance check: every tread's middle on the walking line, and the landing
    const mid = (x, y) => { const a = map(x, y, 0), b = map(x, y, 1); return [(a[0] + b[0]) / 2, y, (a[2] + b[2]) / 2]; };
    const path = [];
    for (let k = 0; k < n; k++) path.push({ p: mid((k + .5) * run, (k + 1) * rise), w: far((k + .5) * run) - near((k + .5) * run) });
    if (landing > 0) path.push({ p: mid(n * run + landing / 2, top), w: far(n * run) - near(n * run), landing: true, len: landing });
    const foot = mid(-.5, 0);
    const instances = placements(def, P, params);
    const stair = { name, geometry: m.arrays(), instances, kind: "spiral-stair", steps: n, rise, run, topOf: top, shell: post, path, foot };
    // (`arrive`: the floor round its top it comes up through -- arrivalFloor; not for one wound round a dome's curve)
    const floor = def.arrive && !def.follow ? arrivalFloor(name, def, P, params, { spiral: { R, top }, soffit }) : [];
    if (!post) return [stair, ...floor];
    const pm = drum(mesh(), r0, r0, -soffit, top + P(def.postAbove, 1), 4 * detailOf(params));
    return [stair, { name: name + " newel", geometry: pm.arrays(), instances, kind: "column", stairPart: name }, ...floor];
  }

  if (def.type === "staircase") {
    // A STAIRCASE OF FLIGHTS AND LANDINGS (build.js staircase): the part itself is the first flight -- `flight`
    // risers, `width` wide -- and its `landing` says what it arrives on and which flights leave from there
    // (`then`: each `from` "ahead", "left", "right" or "back", `at` along that edge, and a flight and landing
    // of its own). `rise` and `run` are every step's, `soffit` the stone under the nosings and the slabs'
    // depth. The imperial stair is one flight, a landing, and two flights back either side of it.
    const run = P(def.run, .32), rise = P(def.rise, .16), soffit = P(def.soffit, .35);
    if (rise < .12 || rise > .22 || run < .25) {
      throw new Error(`its steps are ${(rise * 100).toFixed(1)}cm on a ${(run * 100).toFixed(1)}cm tread -- a climbable flight is 12-22cm on 25cm or more`);
    }
    // `times` on a flight: the flight and its landing again and again, each leaving its landing the same way
    // (`from`, `at`) -- the four flights a storey round a tower's well, for as many storeys as it has. The
    // last copy's landing keeps the node's own `then`. (Not `repeat`: that copies the whole part elsewhere.)
    const unroll = (d) => {
      const k = Math.round(P(d.times, 1));
      if (k <= 1 || !d.landing) return d;
      const next = { ...d, times: k - 1 };
      return { ...d, times: 1, landing: { ...d.landing, then: [{ ...next, from: d.from ?? "ahead", at: d.at ?? 0 }] } };
    };
    const node = (d0) => { const d = unroll(d0); return {
      flight: P(d.flight), width: P(d.width),
      ...(d.landing ? { landing: { depth: P(d.landing.depth), width: P(d.landing.width ?? d.width), shift: P(d.landing.shift, 0),
                                   then: (d.landing.then ?? []).map((c) => ({ ...node(c), from: c.from ?? "ahead", at: P(c.at, 0) })) } } : {}),
    }; };
    // every flight that goes nowhere further ARRIVES on a landing of its own width (unless `landing: false`)
    const ends = (d) => { if (d.landing === undefined && def.landing !== false) d.landing = { depth: d.width, width: d.width, then: [] };
                          else if (d.landing) for (const c of d.landing.then ?? []) ends(c); return d; };
    const { m, flights, path, edges, tops } = staircase(mesh(), ends(node(def)), { run, rise, soffit });
    const st = { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "staircase",
                 topOf: Math.max(...flights.map((f) => f.top)), flights: flights.length, path, edges, foot: flights[0].foot };
    // (`arrive`: the floor beyond its top landings, built under them -- arrivalFloor)
    return def.arrive ? [st, ...arrivalFloor(name, def, P, params, { tops, soffit })] : st;
  }

  if (def.type === "box") {
    // A BLOCK: `width` (x) by `length` (z) by `height`, standing on its placement, centred on it -- a podium, a
    // course of a stylobate, a pier, the straight run of an entablature.
    const w = P(def.width), l = P(def.length), h = P(def.height);
    return solidCourses({ name, geometry: box(mesh(), -w / 2, w / 2, 0, h, -l / 2, l / 2).arrays(), instances: placements(def, P, params), kind: "box" },
                        def, params, h, planPoints({ rect: [w, l] }));
  }

  if (def.type === "coffered-ceiling") {
    // A FLAT COFFERED CEILING: a slab `width` by `length`, `thickness` deep, its soffit cut into `nx` by `nz`
    // coffers (build.js cofferedSurface), placed by the height of its SOFFIT.
    const W = P(def.width), L = P(def.length), T = P(def.thickness, .6), nx = Math.round(P(def.nx)), nz = Math.round(P(def.nz));
    const depth = P(def.depth, T * .5);
    if (!(depth < T * .9)) throw new Error(`coffers ${depth}m deep in a slab ${T}m thick`);
    const m = mesh(), S = (u, v) => [-W / 2 + u * W / nx, 0, -L / 2 + v * L / nz];
    cofferedSurface(m, S, () => [0, 1, 0], { nu: nx, nv: nz, depth, steps: Math.round(P(def.steps, 1)), frame: P(def.frame, .12), step: P(def.step, .07) });
    // the slab round it: its edges carry every coffer's corner, so they meet the soffit's; its top is fanned
    const edge = [...Array.from({ length: nx }, (_, i) => [i, 0]), ...Array.from({ length: nz }, (_, j) => [nx, j]),
                  ...Array.from({ length: nx }, (_, i) => [nx - i, nz]), ...Array.from({ length: nz }, (_, j) => [0, nz - j])];
    const lo = edge.map(([u, v]) => m.vert(...S(u, v))), hi = edge.map(([u, v]) => { const [x, , z] = S(u, v); return m.vert(x, T, z); });
    const c = m.vert(0, T, 0);
    for (let k = 0; k < edge.length; k++) {
      const k2 = (k + 1) % edge.length;
      m.quad(lo[k2], lo[k], hi[k], hi[k2]);
      m.tri(c, hi[k2], hi[k]);
    }
    return { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "ceiling" };
  }

  if (def.type === "colonnade") {
    // A COLONNADE: columns -- base, shaft, capital -- and the entablature they carry. Set out STRAIGHT (`count`
    // at `spacing`, centred on the placement, along x), ROUND (`plan: "round"` on a `radius`: a whole ring or an
    // `arc` with a column at each end) or as a PERISTYLE (`plan: "peristyle"`: `front` by `side` columns round a
    // `width` by `length` rectangle of column axes, the corners counted in both -- a Greek temple's ring).
    // `order` gives the proportions (ORDERS, in the shaft's radius), and anything given outright wins over them;
    // `shaft: "square"` makes pilasters and piers. A column is `height` from the foot of its base to the top of
    // its abacus.
    const order = wordOf(def.order ?? "tuscan", params);   // (a word, or a param holding one: a component's `order`)
    const r = P(def.columnR), H = P(def.height), O = ORDERS[order];
    if (!O) throw new Error(`order "${order}" is not one of ${Object.keys(ORDERS).join(", ")}`);
    const sides = Math.max(3, Math.round(def.sides !== undefined ? P(def.sides) : 4 * detailOf(params)));
    const bh = P(def.base?.h, r * O.base), br = P(def.base?.r, r * O.baseR);
    const ch = P(def.capital?.h, r * O.cap), cr = P(def.capital?.r, r * O.capR), taper = P(def.taper, O.taper);
    if (bh + ch >= H) throw new Error("the base and capital are taller than the column");
    const plan = def.plan ?? "straight";
    let local, stepA = 0, R = 0, spacing = 0, grid = null;
    if (plan === "round") {
      const n = Math.max(1, Math.round(P(def.count)));
      R = P(def.radius);
      const arc = P(def.arc, 360) * Math.PI / 180, full = arc >= 2 * Math.PI - 1e-9;
      stepA = full ? arc / n : arc / Math.max(1, n - 1);
      const a0 = full ? 0 : -arc / 2;
      local = Array.from({ length: n }, (_, i) => { const a = a0 + i * stepA; return [a, R * Math.sin(a), 0, R * Math.cos(a)]; });
    } else if (plan === "peristyle") {
      const nf = Math.round(P(def.front)), ns = Math.round(P(def.side)), W = P(def.width), L = P(def.length);
      local = [];
      for (let i = 0; i < nf; i++) for (let j = 0; j < ns; j++) {
        if (i > 0 && i < nf - 1 && j > 0 && j < ns - 1) continue;          // the ring only
        const onSide = (i === 0 || i === nf - 1) && j > 0 && j < ns - 1;   // turned to face out of the long sides
        local.push([onSide ? Math.PI / 2 : 0, -W / 2 + W * i / (nf - 1), 0, -L / 2 + L * j / (ns - 1)]);
      }
    } else if (plan === "grid") {
      // A HYPOSTYLE: `count` files across (x) at `spacing`, the middle intercolumniation `nave` (wider: the processional
      // way -- an even count leaves the axis between the middle pair), `rows` deep (z) at `rowSpacing`, centred
      const n = Math.max(1, Math.round(P(def.count))), rows = Math.max(1, Math.round(P(def.rows)));
      spacing = P(def.spacing); const nave = P(def.nave, spacing), rs = P(def.rowSpacing, spacing);
      const xs = Array.from({ length: n }, (_, i) => { const k = i - (n - 1) / 2; return k * spacing + Math.sign(k) * (n % 2 ? 0 : (nave - spacing) / 2); });
      grid = { xs, zs: Array.from({ length: rows }, (_, j) => ((rows - 1) / 2 - j) * rs) };
      local = grid.zs.flatMap((z) => xs.map((x) => [0, x, 0, z]));
    } else {
      const n = Math.max(1, Math.round(P(def.count)));
      spacing = P(def.spacing);
      local = Array.from({ length: n }, (_, i) => [0, (i - (n - 1) / 2) * spacing, 0, 0]);
    }
    // each copy of the whole colonnade (its `at`), with each column inside it
    const places = placements(def, P, params);
    const compose = (list) => composeAt(places, list);
    const cols = compose(local);
    const out = [];
    const abH = ch * O.abacus;                      // the abacus's share of the capital; the rest is echinus or bell
    if (def.shaft === "square") {                   // pilasters and piers: square throughout
      if (bh > 0) out.push({ name: name + " bases", geometry: box(mesh(), -br, br, 0, bh, -br, br).arrays(), instances: cols, kind: "box" });
      out.push({ name: name + " shafts", geometry: box(mesh(), -r, r, bh, H - ch, -r, r).arrays(), instances: cols, kind: "box" });
      out.push({ name: name + " capitals", geometry: box(mesh(), -cr, cr, H - ch, H, -cr, cr).arrays(), instances: cols, kind: "box" });
    } else {
      if (bh > 0) out.push({ name: name + " bases", geometry: drum(mesh(), br, br, 0, bh, sides).arrays(), instances: cols, kind: "column" });
      out.push({ name: name + " shafts", geometry: drum(mesh(), r, r * taper, bh, H - ch, sides).arrays(), instances: cols, kind: "column" });
    }
    if (def.shaft !== "square" && O.hathor) {
      // the Hathor block, the sistrum's shrine over it with its lip, the abacus: each a share of the capital's height
      const hs = O.hathor, y0 = H - ch, y1 = y0 + ch * hs.block, y2 = y1 + ch * hs.naos, y3 = y2 + ch * hs.lip, ar = r * taper * .95;
      out.push({ name: name + " capitals", geometry: box(mesh(), -cr, cr, y0, y1, -cr, cr).arrays(), instances: cols, kind: "box" });
      out.push({ name: name + " sistra", geometry: box(mesh(), -r * hs.naosR, r * hs.naosR, y1, y2, -r * hs.naosR, r * hs.naosR).arrays(), instances: cols, kind: "box" });
      out.push({ name: name + " sistrum lips", geometry: box(mesh(), -r * (hs.naosR + .08), r * (hs.naosR + .08), y2, y3, -r * (hs.naosR + .08), r * (hs.naosR + .08)).arrays(), instances: cols, kind: "box" });
      out.push({ name: name + " abaci", geometry: box(mesh(), -ar, ar, y3, H, -ar, ar).arrays(), instances: cols, kind: "box" });
    } else if (def.shaft !== "square" && O.bell) {
      // the bell: its radius swelling from the shaft's top out to `capR`, slowly and then fast -- the flowers opening
      const r0 = r * taper, rings = Math.max(3, detailOf(params)), yb = H - abH, ar = r0 * .95;
      const prof = Array.from({ length: rings + 1 }, (_, k) => { const t = k / rings; return [r0 + (cr - r0) * Math.pow(t, 1.7), H - ch + (yb - H + ch) * t]; });
      out.push({ name: name + " capitals", geometry: lathe(mesh(), prof, sides).arrays(), instances: cols, kind: "column" });
      out.push({ name: name + " abaci", geometry: box(mesh(), -ar, ar, yb, H, -ar, ar).arrays(), instances: cols, kind: "box" });
    } else if (def.shaft !== "square") {
      // the echinus (Doric, Tuscan) or the bell (Corinthian): a flare from the shaft's top toward the abacus
      out.push({ name: name + " capitals", geometry: drum(mesh(), r * taper, cr * O.flare, H - ch, H - abH, sides).arrays(), instances: cols, kind: "column" });
      out.push({ name: name + " abaci", geometry: box(mesh(), -cr, cr, H - abH, H, -cr, cr).arrays(), instances: cols, kind: "box" });
      if (O.volutes) {
        // the Ionic volutes: two scrolls either side of the capital, their axes front to back
        const vr = cr * .32, vy = H - abH - vr * .9, vx = cr - vr * .6;
        const scroll = drum(mesh(), vr, vr, -cr * .85, cr * .85, 8).arrays();
        const p = scroll.position;                // turned on its side: (x, y, z) -> (x, -z, y), a rotation about x
        for (let i = 0; i < p.length; i += 3) { const y = p[i + 1], z = p[i + 2]; p[i + 1] = -z; p[i + 2] = y; }
        out.push({ name: name + " volutes", geometry: scroll, kind: "column",
                   instances: cols.flatMap(([a, x, y, z]) => [-1, 1].map((sx) => [a, x + Math.cos(a) * sx * vx, y + vy, z - Math.sin(a) * sx * vx])) });
      }
    }
    if (def.entablature) {
      // THE ENTABLATURE: architrave and frieze (`h`), then the cornice (`cornice.h`) standing `cornice.out` proud
      // of them; Doric `triglyphs` over every column and every gap between two
      const E = def.entablature, eh = P(E.h), ed = P(E.depth, cr * 2.2);
      const kh = E.cornice ? P(E.cornice.h) : 0, ko = E.cornice ? P(E.cornice.out, eh * .25) : 0;
      if (plan === "round") {
        // round: one bay of a ring per column, centred on it -- so the joints fall between the columns
        const ringBay = (rO, rI, y0, y1) => { const w = stepA * rO; return extrude(wallFace(w, y1 - y0, []), radial(rO, rI, w)).arrays(); };
        const at = compose(local.map(([a]) => [a, 0, H, 0]));
        out.push({ name: name + " entablature", geometry: ringBay(R + ed / 2, R - ed / 2, 0, eh), kind: "ring", instances: at });
        if (kh) out.push({ name: name + " cornice", geometry: ringBay(R + ed / 2 + ko, R - ed / 2, 0, kh), kind: "ring",
                           instances: at.map(([a, x, y, z]) => [a, x, y + eh, z]) });
      } else if (plan === "peristyle") {
        const W = P(def.width) / 2, L = P(def.length) / 2;
        out.push({ name: name + " entablature", geometry: frame(mesh(), [W + ed / 2, L + ed / 2], [W - ed / 2, L - ed / 2], H, H + eh).arrays(),
                   instances: compose([[0, 0, 0, 0]]), kind: "frame" });
        if (kh) out.push({ name: name + " cornice", geometry: frame(mesh(), [W + ed / 2 + ko, L + ed / 2 + ko], [W - ed / 2, L - ed / 2], H + eh, H + eh + kh).arrays(),
                           instances: compose([[0, 0, 0, 0]]), kind: "frame" });
      } else if (grid) {
        // a hypostyle's ARCHITRAVES: one beam over each file of columns, front to back (the roof slabs span across
        // between them) -- or `along: "rows"`, one over each row
        // (`reach` [a, b]: how far each beam runs on past the first row and the last -- the front row's, and the last's
        //  to the wall it is laid on; negative stops it short. Files: from the front row back; rows: from the left file)
        const rowsAlong = E.along === "rows", [ra, rb] = E.reach ? E.reach.map((v) => P(v)) : [P(E.over, cr * 2) / 2, P(E.over, cr * 2) / 2];
        const lo = rowsAlong ? grid.xs[0] - ra : grid.zs[grid.zs.length - 1] - rb, hi = rowsAlong ? grid.xs[grid.xs.length - 1] + rb : grid.zs[0] + ra;
        out.push({ name: name + " architraves", kind: "box", instances: compose((rowsAlong ? grid.zs : grid.xs).map((c) => [0, rowsAlong ? 0 : c, H, rowsAlong ? c : 0])),
                   geometry: (rowsAlong ? box(mesh(), lo, hi, 0, eh, -ed / 2, ed / 2) : box(mesh(), -ed / 2, ed / 2, 0, eh, lo, hi)).arrays() });
      } else {
        const len = (local.length - 1) * spacing + P(E.over, cr * 2);
        out.push({ name: name + " entablature", geometry: box(mesh(), -len / 2, len / 2, H, H + eh, -ed / 2, ed / 2).arrays(),
                   instances: compose([[0, 0, 0, 0]]), kind: "box" });
        if (kh) out.push({ name: name + " cornice", geometry: box(mesh(), -len / 2 - ko, len / 2 + ko, H + eh, H + eh + kh, -ed / 2 - ko, ed / 2 + ko).arrays(),
                           instances: compose([[0, 0, 0, 0]]), kind: "box" });
      }
      if (E.triglyphs && plan !== "round") {
        // over each column and each gap, on every outer face, the upper half of the band (the frieze)
        const tw = P(E.triglyphs.w, r * 1.1), td = P(E.triglyphs.d, .12), fh = eh * .5, y = H + eh - fh / 2;
        const spots = [];
        const row = (from, to, count, fixed, axis) => {           // `count` columns from `from` to `to`
          for (let k = 0; k <= 2 * (count - 1); k++) {
            const c = from + (to - from) * k / (2 * (count - 1));
            spots.push(axis === "x" ? [0, c, y, fixed] : [Math.PI / 2, fixed, y, c]);
          }
        };
        if (plan === "peristyle") {
          const W = P(def.width) / 2, L = P(def.length) / 2, nf = Math.round(P(def.front)), ns = Math.round(P(def.side));
          for (const s of [-1, 1]) { row(-W, W, nf, s * (L + ed / 2), "x"); row(-L, L, ns, s * (W + ed / 2), "z"); }
        } else for (const s of [-1, 1]) row(local[0][1], local[local.length - 1][1], local.length, s * ed / 2, "x");
        out.push({ name: name + " triglyphs", geometry: box(mesh(), -tw / 2, tw / 2, -fh / 2, fh / 2, -td / 2, td / 2).arrays(),
                   instances: compose(spots), kind: "box" });
      }
    }
    return out;
  }

  if (def.type === "pyramid") {
    // A PYRAMID (2026-10-05): a square `base`, `height` to the apex, its faces cut in bands -- the CORE below `casing`
    // (the stepped limestone the casing was robbed from), the CASING from there up (the white Tura limestone Khafre's
    // keeps at its top), the CAP from `cap` metres under the apex (the gilded pyramidion) -- each band its own part, so
    // a finish names them. `entrance` { width, height }: a door at the foot of the north face (+z) and a level PASSAGE
    // in from it to the burial CHAMBER (`chamber` { width (x), length (z), height }) at the pyramid's middle -- a closed
    // room (walls, floor, ceiling, all facing in, each wall its own part: north, south, east, west) whose north wall the
    // passage pierces. The rest of the inside is solid stone nobody sees, so it is left hollow.
    const Bh = P(def.base) / 2, H = P(def.height), yc = def.casing !== undefined ? P(def.casing) : H, yk = H - P(def.cap, 0);
    const half = (y) => Bh * (1 - y / H);
    const parts = [], at = placements(def, P, params);
    // (every part is a SHELL: the bands are one mass's faces cut where the stone changes, the rooms its hollows -- each
    //  an open sheet whose edges are the next one's, as a pendentive's are)
    const add = (suffix, m, kind = "pyramid") => { const a = m.arrays(); if (a.index.length) parts.push({ name: `${name} ${suffix}`, geometry: a, instances: at, kind, shell: true }); };
    // a triangle turned to face `want` (outward, or into a room)
    const tri = (m, A, B, C, want) => {
      const u = [B[0] - A[0], B[1] - A[1], B[2] - A[2]], v = [C[0] - A[0], C[1] - A[1], C[2] - A[2]];
      const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
      const a = m.vert(...A), b = m.vert(...B), c = m.vert(...C);
      if (n[0] * want[0] + n[1] * want[1] + n[2] * want[2] >= 0) m.tri(a, b, c); else m.tri(a, c, b);
    };
    const quad = (m, A, B, C, D, want) => { tri(m, A, B, C, want); tri(m, A, C, D, want); };
    // the four sides: (s across the face, y up) -> 3D; side 0 the north face (+z)
    const SIDES = [[(s, o) => [s, o], [0, 0, 1]], [(s, o) => [o, -s], [1, 0, 0]], [(s, o) => [-s, -o], [0, 0, -1]], [(s, o) => [-o, s], [-1, 0, 0]]];
    const ent = def.entrance ? { w: P(def.entrance.width) / 2, h: P(def.entrance.height) } : null;
    const tA = Math.tan(P(def.slope, 26) * Math.PI / 180);
    if (ent) ent.door = ent.h / (1 + tA * Bh / H);   // (the door's height: where the passage's sloping ceiling meets the face)
    const bands = [["core", 0, Math.min(yc, yk)], ["casing", Math.min(yc, yk), yk], ["cap", yk, H]];
    for (const [band, y0, y1] of bands) {
      if (y1 - y0 < 1e-6) continue;
      const m = mesh();
      SIDES.forEach(([to3, out], k) => {
        const p3 = (s, y) => { const [x, z] = to3(s, half(y)); return [x, y, z]; };
        const want = [out[0], .6, out[2]];
        if (k === 0 && ent && y0 === 0 && ent.door < y1) {
          // the north face's foot, cut by the door: its outline in (s, y), ear-clipped
          const pts = [[-half(0), 0], [-ent.w, 0], [-ent.w, ent.door], [ent.w, ent.door], [ent.w, 0], [half(0), 0], [half(y1), y1], [-half(y1), y1]];
          for (const [a, b, c] of earClip(pts, pts.map((_, i) => i))) tri(m, p3(...pts[a]), p3(...pts[b]), p3(...pts[c]), want);
        } else quad(m, p3(-half(y0), y0), p3(half(y0), y0), p3(half(y1), y1), p3(-half(y1), y1), want);
      });
      add(band, m, "roof");
    }
    if (ent) {
      // THE DESCENDING PASSAGE (Khufu's and Khafre's go down at about 26 degrees from the north face into the rock): from
      // the door at the face's foot down at `slope` to the chamber's floor at `depth` under the ground, then LEVEL to the
      // chamber, which is cut in the rock under the pyramid's middle. The door is as tall as the face lets the sloping
      // ceiling meet it. Each side wall is one outline (face, slope, level, the chamber) ear-clipped.
      const C0 = def.chamber ?? { width: 10, length: 5, height: 5.8 }, cw = P(C0.width) / 2, cl = P(C0.length) / 2, ch = P(C0.height), w = ent.w, h = ent.h, lift = .02;
      const zF = half(0);
      const yd = -Math.min(P(def.depth, 8), Math.max(1.5, (zF - cl - 2) * tA)), zB = zF + yd / tA;   // (the slope's foot; the level run from there to the chamber)
      const hd = ent.door, zD = half(hd);
      const pw = mesh(), pc = mesh(), pf = mesh();
      const side = [[zF, 0], [zB, yd], [cl, yd], [cl, yd + h], [zB, yd + h], [zD, hd]];   // (z, y): the passage's side outline
      for (const sx of [-1, 1]) for (const [a, b, c] of earClip(side, side.map((_, i) => i))) {
        const V = (q) => [sx * w, side[q][1], side[q][0]];
        tri(pw, V(a), V(b), V(c), [-sx, 0, 0]);
      }
      quad(pc, [-w, yd + h, cl], [w, yd + h, cl], [w, yd + h, zB], [-w, yd + h, zB], [0, -1, 0]);
      quad(pc, [-w, yd + h, zB], [w, yd + h, zB], [w, hd, zD], [-w, hd, zD], [0, -1, 0]);
      quad(pf, [-w, yd + lift, cl], [w, yd + lift, cl], [w, yd + lift, zB], [-w, yd + lift, zB], [0, 1, 0]);
      quad(pf, [-w, yd + lift, zB], [w, yd + lift, zB], [w, lift, zF], [-w, lift, zF], [0, 1, 0]);
      add("passage walls", pw); add("passage ceiling", pc); add("passage floor", pf);
      // the chamber, in the rock at the passage's level: four walls facing in, the north one with the passage's door
      const north = mesh(), south = mesh(), east = mesh(), west = mesh(), roof = mesh(), floor = mesh(), y0 = yd, y1 = yd + ch;
      const npts = [[-cw, y0], [-w, y0], [-w, y0 + h], [w, y0 + h], [w, y0], [cw, y0], [cw, y1], [-cw, y1]];
      for (const [a, b, c] of earClip(npts, npts.map((_, i) => i))) tri(north, [npts[a][0], npts[a][1], cl], [npts[b][0], npts[b][1], cl], [npts[c][0], npts[c][1], cl], [0, 0, -1]);
      quad(south, [-cw, y0, -cl], [cw, y0, -cl], [cw, y1, -cl], [-cw, y1, -cl], [0, 0, 1]);
      quad(east, [cw, y0, -cl], [cw, y0, cl], [cw, y1, cl], [cw, y1, -cl], [-1, 0, 0]);
      quad(west, [-cw, y0, -cl], [-cw, y0, cl], [-cw, y1, cl], [-cw, y1, -cl], [1, 0, 0]);
      quad(roof, [-cw, y1, -cl], [cw, y1, -cl], [cw, y1, cl], [-cw, y1, cl], [0, -1, 0]);
      quad(floor, [-cw, y0 + lift, -cl], [cw, y0 + lift, -cl], [cw, y0 + lift, cl], [-cw, y0 + lift, cl], [0, 1, 0]);
      add("chamber north wall", north); add("chamber south wall", south); add("chamber east wall", east); add("chamber west wall", west);
      add("chamber ceiling", roof); add("chamber floor", floor);
    }
    return parts;
  }

  if (def.type === "shikhara") {
    // A NAGARA TOWER (shikhara.js): `width` across its karnas' faces, `height` to its shoulder; its ratha plan (`rathas`,
    // `step`, `bhadra`), its curve (`top`, `bend`), its storeys (`bhumis`, `band`), the copies of it on its faces
    // (`tiers`: [{ scale, lift, out }], `nest` deep) and on its corners (`corners`: { scale, at }). Its body, each tier
    // of copies and its crowns are parts of their own -- in the order they are raised: the body, the copies, the crowns.
    const spec = shikharaOf(def, P, params), meshes = new Map(), put = (k) => { let m = meshes.get(k); if (!m) meshes.set(k, m = mesh()); return m; };
    shikharaMesh(put, spec);
    const instances = placements(def, P, params), rank = (k) => (k === "body" ? 0 : k === "crown" ? 3 : k === "karna shringas" ? 2 : 1);
    return [...meshes.keys()].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b))
      .map((k) => ({ name: k === "body" ? name : `${name} ${k}`, geometry: meshes.get(k).arrays(), instances, kind: k === "crown" ? "column" : "prism" }));
  }

  if (def.type === "samvarana") {
    // A HALL'S STEPPED ROOF (shikhara.js samvaranaMesh): `width` (x) by `length` (z) its lowest course, `rise` to its top, `tiers`
    // courses narrowing to `top` of the width, its ratha plan (`rathas`, `step`, `bhadra`), `bells` on its courses
    // (false: a phamsana), the great bell, amalaka and kalasha over it -- in the order they are raised.
    const spec = samvaranaOf(def, P, params), meshes = new Map(), put = (k) => { let m = meshes.get(k); if (!m) meshes.set(k, m = mesh()); return m; };
    samvaranaMesh(put, spec);
    const instances = placements(def, P, params);
    return ["body", "bells", "crown"].filter((k) => meshes.has(k))
      .map((k) => ({ name: k === "body" ? name : `${name} ${k}`, geometry: meshes.get(k).arrays(), instances, kind: k === "body" ? "roof" : "column" }));
  }

  if (def.type === "helm") {
    // A RHENISH HELM (helm.js): `sides` (4) round a circumradius `radius` -- or a square's `width` -- its gables at `pitch`,
    // the point where its rhombi say; `frieze`: a rising arched frieze up every gable (lombard.js), a moulding of its own
    const n = Math.round(P(def.sides, 4)), R = def.width !== undefined ? P(def.width) / 2 / Math.sin(Math.PI / n) : P(def.radius);
    const fz = def.frieze ? { m: mesh(), spec: def.frieze === true ? {} : Object.fromEntries(Object.entries(def.frieze).filter(([k]) => !k.startsWith("_")).map(([k, v]) => [k, P(v)])) } : null;
    const { m, H } = helmMesh(mesh(), { n, R, pitch: P(def.pitch, 60), turn: P(def.turn, n === 4 ? .5 : 0), frieze: fz });
    const helm = { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "roof", ridge: H };
    return fz ? [helm, { name: name + " frieze", geometry: fz.m.arrays(), instances: helm.instances, kind: "moulding", shell: true }] : helm;
  }

  if (def.type === "prism") {
    // A PRISM on a plan (build.js planPoints: `rect`, `chamfer`, `sides` + `radius`, or `points`), `height` tall:
    // a plinth, a platform, the solid core of a tower
    // `plan.well` cuts a stairwell through it -- `radius` (and `sides`) or `rect` [w, l], `at` [x, z]: the floor a spiral
    // comes up through. `slope` [sx, sz] tilts its top: `height` at the plan's origin, rising sx a metre along x and sz
    // along z -- a mass whose top is a plane, as the wedge behind a lean-to's end is (it takes the roof's own fall)
    const pts = planPoints(planOf(def.plan, P)), wl = def.plan.well;
    const H = P(def.height), [sx, sz] = (def.slope ?? [0, 0]).map((v) => P(v)), topAt = sx || sz ? (x, z) => H + sx * x + sz * z : H;
    const well = wl && wellPoints({ at: (wl.at ?? [0, 0]).map((v) => P(v)), ...(wl.rect ? { rect: wl.rect.map((v) => P(v)) } : { radius: P(wl.radius), sides: P(wl.sides, 4 * detailOf(params)), turn: P(wl.turn, 0) }) });
    // (its well railed where it drops: wellEdges)
    return solidCourses({ name, geometry: prismMesh(mesh(), pts, 0, topAt, well).arrays(), instances: placements(def, P, params), kind: "prism",
                          ...(well ? { edges: wellEdges(well, H), railing: def.railing } : {}) }, def, params, H, pts);
  }

  if (def.type === "enclosure") {
    // WALLS ROUND A PLAN: `thickness` thick and `height` tall on the outline of `plan`, each face with openings.
    // `openings` is what every face has (a pattern or a list, laid out centred on the face) -- or `tiers`, bands
    // stacked from the ground, each { h, openings } -- and `faces` overrides either by face number (counted round
    // the plan), by label ("main:1") or by family ("main", "chamfer"): the most particular wins; `[]` is blind.
    const pts = planPoints(planOf(def.plan, P)), n = pts.length, t = P(def.thickness), h = P(def.height);
    const faces = pts.map((p0, i) => {
      const p1 = pts[(i + 1) % n], L = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
      // the most particular wins: its number, its label ("main:1"), its label's family ("main"), then every face's
      const lab = pts.labels[i], fam = lab.split(":")[0], F = def.faces ?? {};
      const spec = [F[i], F[lab], F[fam]].find((v) => v !== undefined) ?? (def.tiers ?? def.openings);
      return withLombard(tiersOf(spec, h, L, P, params).map((t) => ({ ...t, openings: glazed(t.openings, flagOf(def.glass, params)) })), def, params);
    });
    const g = mesh(), plan = orderPlan(def, params, h, t, faces);
    const part = withGlass({ name, geometry: enclosureMesh(mesh(), pts, t, faces.map((f) => withOrderTops(plan, f)), g).arrays(), instances: placements(def, P, params), kind: "enclosure",
                            lintels: lintelsOf(pts, faces, t, true) }, g);
    if (!def.courses?.inner)
      return withCourses(part, def, params, h, t, Object.assign(pts.map((q) => [q[0], q[1]]), { labels: pts.labels }), faces, true, [], plan);
    // (`courses.inner`: along the INSIDE face -- a courtyard's walls, whose face to be seen is the inner one. Its line
    //  is the inner outline walked backwards, so the inside is on its left; segment k is face j walked from its end,
    //  and an opening at x on the face comes through at u(x) from its start)
    const inn = insetPoints(pts, t), thru = innerAlong(pts, t, faces), ks = pts.map((_, k) => (2 * n - 2 - k) % n);
    const line = Object.assign(ks.map((j) => [inn[(j + 1) % n][0], inn[(j + 1) % n][1]]), { labels: ks.map((j) => pts.labels[j]), faces: ks });
    return withCourses(part, def, params, h, t, line, ks.map((j) => faces[j]), true,
                       ks.map((j) => ({ L: thru[j].L, x: (x) => thru[j].Li - thru[j].u(x) })));
  }

  if (def.type === "flyer") {
    // A FLYING BUTTRESS: across `span` from the pier (at the placement) to the wall it props, its soffit a rampant
    // quarter-arch from `low` at the pier to `high` at the wall, its back straight from `top0` to `top1`, `width`
    // thick. Turned by its yaw so it reaches along +x.
    const m = flyerMesh(mesh(), { span: P(def.span), low: P(def.low), high: P(def.high), top0: P(def.top0), top1: P(def.top1),
                                  width: P(def.width), per90: detailOf(params) });
    return { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "flyer" };
  }

  if (def.type === "basilica") {
    // A VAULTED CHURCH AS ITS SKELETON (gothic.js): `bays` of `bayLen` down a nave `naveW` between the arcade's centre
    // lines, aisles `aisleW` from there to the outer wall, and an apse of `apse` sides (0: a flat east end) on the same
    // two lines; the piers, arches, rib vaults, buttresses, flyers and roofs all follow from those and the springing.
    // Every number may be an expression; `skipAisle` / `skipOuter` are [[from, to]] bays counted from the west, and
    // `transept` [from, to] the bays the crossing spans, its arms reaching `arm` past the aisle walls. Its heights are
    // worked out, not given: a part stands on one with `atop` and `atopLevel` (gothic.js: "wallTop", "ridge", ...).
    const instances = placements(def, P, params);
    return basilica(basilicaOf(def, P, params), detailOf(params)).parts.map((q) => ({ ...q, name: `${name}/${q.name}`, geometry: q.geometry.arrays(), instances }));
  }

  if (def.type === "ward") {
    // A FORTIFIED WARD (castle.js): the curtain round `plan` (its outer face), the towers flanking its corners and its
    // long faces, the gate between its pair, the crenellated wall walk running through the towers, their floors,
    // loops, decks and newel stairs -- all worked out from the curtain's measures and written as the engine's own parts
    const defs = wardDefs(def, P, planOf(def.plan, P)), places = placements(def, P, params);
    return Object.keys(defs).flatMap((k) => [buildPart(k, defs, params)].flat())
      .map((q) => ({ ...q, name: `${name}/${q.name}`, instances: composeAt(places, q.instances) }));
  }

  if (def.type === "court") {
    // A RING OF ROOMS ROUND A COURTYARD -- a cloister, a palace's quadrangle, a castle's court -- as ONE thing, so its
    // floor plan is connected all the way round: outer walls on `plan` (rect, sides + radius, points), courtyard walls
    // `depth` in, `storeys` of `storeyH`, a window every `axis` metres on every face, a row of doors from the court
    // into the rooms, continuous floors on every storey, a dog-leg stair up every storey on side `stairFace`
    // (the floors cut round it), a GATE through both walls on side `gate.face` into the court, and a roof over every
    // side (`roof.form`, `roof.pitch`). It is made of the engine's own parts -- enclosures, prisms, a staircase, roofs
    // -- written here and built as any other part, and named "<court>/<part>". `tracery` fills its windows (tracery.js:
    // a sash's glazing bars are { style: "bars" }).
    const O = planPoints(planOf(def.plan, P)), n = O.length;
    const D = P(def.depth), N = Math.max(1, Math.round(P(def.storeys, 1))), H = P(def.storeyH, 4.5), t = P(def.thickness, .9);
    const slab = P(def.slab, .35), axis = P(def.axis, 3.6), winW = P(def.winW, 1.3), sill = P(def.sill, .95), winH = P(def.winH, 2.3);
    const doorW = P(def.doorW, 1.6), doorH = P(def.doorH, 3.0), head = def.head ?? { profile: "segmental", seg: .35 };
    const gate = def.gate ? { face: Math.round(P(def.gate.face, 0)), width: P(def.gate.width, 3.6), height: Math.min(P(def.gate.height, 4.2), H - .3),
                              head: def.gate.head ?? { profile: "semicircular" } } : null;
    const sf = Math.round(P(def.stairFace, gate && gate.face === 1 ? 2 : 1)) % n;
    const courtLine = insetPoints(O, D - t), roomsOut = insetPoints(O, t), roomsIn = insetPoints(O, D - t), court = insetPoints(O, D);
    const len = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
    const row = (L, w, sl, h, extra = {}) => {                 // a centred row of openings, one per `axis` metres
      let k = Math.floor(L / axis - .5);
      if (extra.middle && k % 2 === 0) k -= 1;                 // (a middle opening needs an odd row)
      return k < 1 ? (extra.middle ? [{ at: 0, width: extra.middle.width, sill: 0, springing: extra.middle.springing, head }] : [])
        : { pattern: String(k), width: w, gap: axis - w, sill: sl, springing: sl + h, head, ...(def.tracery ? { tracery: def.tracery } : {}), ...extra };
    };
    // (the gate's head is its own -- round unless it says -- and its springing is worked so its crown is `height`, within
    //  the ground storey)
    const gateOf = (i) => gate && gate.face === i ? { middle: { width: gate.width, sill: 0, head: gate.head, glass: false,
      springing: gate.height - archCurve(gate.width / 2, headOf(gate.head, params)).reduce((m, [, y]) => Math.max(m, y), 0) } } : {};
    // (`surround`: how its windows are dressed -- surround.js -- one for all, or a list, storey by storey)
    //  (on the court walls, on their back: the face the court sees)
    const dress = (k, side) => { const v = Array.isArray(def.surround) ? def.surround[k] : def.surround;
                                 return v ? { surround: { ...(v === true ? {} : v), ...(side ? { side: 1 } : {}) } } : {}; };
    const tiers = (L, i, ground, side) => Array.from({ length: N }, (_, k) => ({ ...(k < N - 1 ? { h: H } : {}),
      openings: k === 0 ? ground(L, i) : row(L, winW, sill, winH, dress(k, side)) }));
    // JOINS: where another building stands against an outer face (`face`, `at` from its middle, `width` along it) the
    // face has no windows -- they would look into its wall -- and, with `door`, a doorway through on the ground storey:
    // the way from the court's rooms into it (a church's crossing against the cloister's wing)
    const joins = (def.joins ?? []).map((j) => ({ face: Math.round(P(j.face)), at: P(j.at, 0), width: P(j.width),
      door: j.door ? { width: P(j.door.width, 2.4), height: P(j.door.height, 3.4), head: j.door.head ?? { profile: "semicircular" } } : null }));
    const joinedTiers = (L, i) => {
      const js = joins.filter((j) => j.face === i);
      const k = Math.floor(L / axis - .5), at = Array.from({ length: Math.max(0, k) }, (_, q) => (q - (k - 1) / 2) * axis)
        .filter((x) => js.every((j) => Math.abs(x - j.at) > j.width / 2 + winW / 2 + .3));
      const wins = (q) => at.map((x) => ({ at: x, width: winW, sill, springing: sill + winH, head, ...dress(q) }));
      const doors = js.filter((j) => j.door).map((j) => ({ at: j.at, width: j.door.width, sill: 0, glass: false, head: j.door.head,
        springing: j.door.height - archCurve(j.door.width / 2, headOf(j.door.head, params)).reduce((m, [, y]) => Math.max(m, y), 0) }));
      return Array.from({ length: N }, (_, q) => ({ ...(q < N - 1 ? { h: H } : {}), openings: q === 0 ? [...wins(0), ...doors] : wins(q) }));
    };
    const defs = {};
    defs["outer walls"] = { type: "enclosure", plan: { points: O }, thickness: t, height: N * H, ...(def.glass !== undefined ? { glass: def.glass } : {}),   // (glazed or not: the court's say)
      faces: Object.fromEntries(O.map((p, i) => [i, joins.some((j) => j.face === i) ? joinedTiers(len(p, O[(i + 1) % n]), i)
                                                   : tiers(len(p, O[(i + 1) % n]), i, (L, j) => row(L, winW, sill, winH, { ...dress(0), ...gateOf(j) }))])),
      // (its courses stop where a joined building stands against a face)
      ...(def.courses ? { courses: { ...(def.courses === true ? {} : def.courses), clear: Object.fromEntries(O.map((p, i) => [i,
        joins.filter((j) => j.face === i).map((j) => { const L = len(p, O[(i + 1) % n]); return [L / 2 + j.at - j.width / 2, L / 2 + j.at + j.width / 2]; })])) } } : {}) };
    defs["court walls"] = { type: "enclosure", plan: { points: courtLine }, thickness: t, height: N * H, ...(def.glass !== undefined ? { glass: def.glass } : {}),
      faces: Object.fromEntries(courtLine.map((p, i) => [i, tiers(len(p, courtLine[(i + 1) % n]), i,
        (L, j) => row(L, doorW, 0, doorH - doorW / 2, { ...dress(0, true), ...gateOf(j) }), true)])),
      // (round the court, on the walls' inner face: the one the court sees)
      ...(def.courses ? { courses: { ...(def.courses === true ? {} : def.courses), inner: true } } : {}) };
    // the floors: a trapezoid per side between the walls; on the stair's side, three pieces round its well
    const run = .28, f = Math.round(H / .34), SW = 2.7, Ls = 2.8 + f * run, dv = D - 2 * t;
    const trap = (i) => [roomsOut[i], roomsOut[(i + 1) % n], roomsIn[(i + 1) % n], roomsIn[i]];
    const o0 = roomsOut[sf], o1 = roomsOut[(sf + 1) % n], Lo = len(o0, o1);
    const e = [(o1[0] - o0[0]) / Lo, (o1[1] - o0[1]) / Lo];
    let m = [-e[1], e[0]];
    const c0 = roomsIn[sf];
    if ((c0[0] - o0[0]) * m[0] + (c0[1] - o0[1]) * m[1] < 0) m = [e[1], -e[0]];
    const at = (u, v) => [o0[0] + e[0] * u + m[0] * v, o0[1] + e[1] * u + m[1] * v];
    const u0 = Lo / 2 - Ls / 2, u1 = u0 + Ls;
    const well = [[o0, at(u0, 0), at(u0, dv), roomsIn[sf]], [at(u1, 0), o1, roomsIn[(sf + 1) % n], at(u1, dv)],
                  [at(u0, SW), at(u1, SW), at(u1, dv), at(u0, dv)]];
    const floorPlans = [...O.map((_, i) => i).filter((i) => i !== sf).map(trap), ...well];
    floorPlans.forEach((pts, i) => { defs[`floor ${i + 1}`] = { type: "prism", plan: { points: pts }, height: slab, at: [[0, H - slab, 0, 0]],
                                                               repeat: { count: N - 1, step: [0, H, 0, 0] } }; });
    O.forEach((_, i) => { defs[`attic floor ${i + 1}`] = { type: "prism", plan: { points: trap(i) }, height: slab, at: [[0, N * H - slab, 0, 0]] }; });
    // the stair: the palace wing's dog-leg, its flights along the side, stacked storey over storey
    const s_ = -e[1], c_ = e[0];                              // (a placement's yaw: local x along e, local z to (s, c))
    const vOrigin = (s_ * m[0] + c_ * m[1]) < 0 ? 2.05 : .65;
    const so = at(u0 + 1.4, vOrigin);
    defs["stair"] = { type: "staircase", rise: H / (2 * f), run, soffit: .3, flight: f, width: 1.3,
      landing: { depth: 1.4, width: SW, shift: .7, then: [{ from: "back", at: .7, flight: f, width: 1.3, landing: { depth: 1.4, width: SW, shift: .7 } }] },
      place: [[so[0], 0, so[1], Math.atan2(s_, c_)]], repeat: { count: N - 1, step: [0, H, 0, 0] } };
    // a roof over every side, along its outer edge -- its eaves reaching past the cornice under them
    const crown = coursesOf(coursesSpec(def.courses, params), N * H, t).filter((c) => c.y + c.h > N * H - 1e-6);
    const eaves = Math.max(P(def.roof?.overhang, .4), ...crown.map((c) => c.out + .1));
    O.forEach((p, i) => {
      const q = O[(i + 1) % n], L = len(p, q), ex = (q[0] - p[0]) / L, ez = (q[1] - p[1]) / L;
      let mx = -ez, mz = ex;
      const ci = court[i];
      if ((ci[0] - p[0]) * mx + (ci[1] - p[1]) * mz < 0) { mx = ez; mz = -ex; }
      defs[`roof ${i + 1}`] = { type: "roof", form: wordOf(def.roof?.form ?? "hip", params), width: D, length: L, pitch: P(def.roof?.pitch, 40),
        overhang: eaves, at: [[(p[0] + q[0]) / 2 + mx * D / 2, N * H, (p[1] + q[1]) / 2 + mz * D / 2, Math.atan2(ex, ez)]] };
    });
    const places = placements(def, P, params);
    return Object.keys(defs).flatMap((k) => [buildPart(k, defs, params)].flat())
      .map((q) => ({ ...q, name: `${name}/${q.name}`, instances: composeAt(places, q.instances) }));
  }

  if (def.type === "component") {
    // ANOTHER DEFINITION, placed: `use` names it (a path under assets/architecture), `params` are its own, given
    // as expressions over THIS building's params, `build` may pick some of its parts. Every part it makes is
    // drawn at every one of this part's placements (at / repeat / spiral), under this part's name.
    const sub = LIB.get(def.use);
    if (!sub) throw new Error(`component "${def.use}" is not loaded (registerDocs / loadUses)`);
    const given = {};
    for (const [k, v] of Object.entries(def.params ?? {})) if (!k.startsWith("_")) { const x = value_(v, params); given[k] = typeof x === "string" ? wordOf(x, params) : x; }   // (a word param passed by name: the fence's `style` is the yard's `fence`)
    if (given.detail === undefined) given.detail = params.detail;
    if (given.furnish === undefined && params.furnish !== undefined) given.furnish = params.furnish;   // (and the period's furniture: the item swaps)
    // (the component's own railings are left to the building: a wall of the building's may stand where it had none)
    const asm0 = assemble(sub, { ...given, ...(def.build ? { build: def.build } : {}), fit: false });   // (its furniture fitted in the whole building)
    const asm = { ...asm0, parts: asm0.parts.filter((q) => q.kind !== "railing") };
    const places = placements(def, P, params);
    return asm.parts.map((q) => ({ ...q, name: `${name}/${q.name}`, instances: composeAt(places, q.instances) }));
  }

  if (def.type === "zone") {
    // A FLOOR AREA FURNISHED BY ITS USE: `zone` names a rule of assets/architecture/furnishing.json (seating, altar,
    // organ, lectern, choir), `w` across (the zone's z), `d` deep (its x), `h` the headroom over it, `at` its centre
    // and turn -- its +x the way the furniture faces, toward the altar. The rule says what fills it: one component
    // or item at the centre, or rows of a component from the back, split by an aisle in a wide zone. A church says
    // where its nave seats, its altar and its organ ARE; what they are is the rule's -- change the pew for a chair
    // there, not in every church.
    const rule = FURNISHING.zones[def.zone];
    if (!rule) throw new Error(`no furnishing rule "${def.zone}"`);
    const w = P(def.w, 2), d = P(def.d, 2), h = P(def.h, 6), ctx = { ...params, w, d, h };
    const defs = {};
    const fill = (k, x, z, L) => {
      const given = {};
      for (const [pk, pv] of Object.entries(rule.params ?? {})) given[pk] = value_(pv, { ...ctx, L });
      defs[k] = rule.item ? { type: "item", item: rule.item, params: given, at: [[x, 0, z, rule.yaw ?? 0]], ...(rule.markers !== undefined ? { markers: rule.markers } : {}) }
                          : { type: "component", use: rule.use, params: given, at: [[x, 0, z, rule.yaw ?? 0]] };
    };
    if (rule.kind === "rows") {
      const pitch = rule.pitch ?? 1.6, margin = rule.margin ?? .3, aisle = w > (rule.aisleOver ?? 1e9) ? rule.aisle ?? 1.5 : 0;
      const n = Math.max(0, Math.floor((d - margin) / pitch));
      const halves = aisle ? [[-(w / 4 + aisle / 4), w / 2 - aisle / 2 - margin], [w / 4 + aisle / 4, w / 2 - aisle / 2 - margin]] : [[0, w - 2 * margin]];
      for (let i = 0; i < n; i++) halves.forEach(([z, L], j) => fill(`row ${i + 1}${aisle ? j ? " right" : " left" : ""}`, -d / 2 + margin + (i + .5) * pitch, z, L));
    } else fill(def.zone, 0, 0, w);
    const places = placements(def, P, params);
    return Object.keys(defs).flatMap((k) => [buildPart(k, defs, params)].flat()).map((q) => ({ ...q, name: `${name}/${q.name}`, instances: composeAt(places, q.instances) }));
  }

  if (def.type === "item") {
    // A THING OUT OF assets/items: a chair, a bed, a table, a chest, a lectern -- `item` its path, `params` its own
    // (expressions over this building's, as a component's are), `seed` which one of its kind, `materials` its roles
    // (the town's oak or walnut). The building holds only its BOX -- the walk goes round it, as it went round the
    // blocks rooms were furnished with before (`solid: false`: none, for what stands on something else) -- and
    // architecture.js draws the item itself, in its own materials. Its MARKERS (a seat, a bed, the places at a
    // table) become the building's at every placement of the part; `markers` keeps them all (true), none (false)
    // or those of the roles listed (a table's benches: their seats, the table has the places), and `data` is added
    // to each (a bed upstairs: its storey, over this building's params).
    // A PERIOD'S OWN (furnishing.json `swaps`): under the building's `furnish` word the item is another -- its own
    // params over the placement's, its own markers, turned `turn` about its foot (the Ottoman's divan for the bench)
    const swap = params.furnish !== undefined ? FURNISHING.swaps?.[params.furnish]?.[def.item] ?? null : null;
    const given = {};
    for (const [k, v] of Object.entries(def.params ?? {})) if (!k.startsWith("_")) given[k] = value_(v, params);
    for (const [k, v] of Object.entries(swap?.params ?? {})) given[k] = value_(v, params);
    const ref = { path: swap?.item ?? def.item, seed: def.seed !== undefined ? P(def.seed) : 1, params: given, materials: swap ? null : def.materials ?? null };
    const places0 = placements(def, P, params), places = swap?.turn ? composeAt(places0, [[swap.turn, 0, 0, 0]]) : places0;
    const it = itemOf(ref), [lo, hi] = [it.bounds.lo, it.bounds.hi];
    const keep = swap?.markers ?? def.markers ?? true, more = {};
    for (const [k, v] of Object.entries(def.data ?? {})) if (!k.startsWith("_")) more[k] = typeof v === "string" || typeof v === "number" ? value_(v, params) : v;
    return [{ name, geometry: def.solid === false ? NOTHING() : box(mesh(), lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]).arrays(), instances: places, kind: "item", item: ref },
            ...it.markers.filter((m) => keep === true || (Array.isArray(keep) && keep.includes(m.role))).map((m, i) => ({
              name: `${name}/${m.role} ${i + 1}`, geometry: NOTHING(), instances: composeAt(places, [[m.yaw, ...m.at]]), kind: "marker", role: m.role, data: { ...m.data, ...more } }))];
  }

  if (def.type === "marker") {
    // A MARKER: nothing drawn -- a PLACE the game uses: a bed, a door, a seat, a work spot, a fire, the route up a
    // stair (`role`, and its `data`: a door's width and height, a work spot's gesture and tool...). It is a part
    // like any other so that every placement a part has carries it: a component's copies, a repeat, the base's
    // lift, the site's turn -- a bed stands where its bed frame stands, whatever put it there. architecture.js
    // archBuilding reads the markers out as the site's life (beds, doors, folkSpots, seats, fires, ways).
    const data = {};
    // (a word or a number read over the params -- and so inside a table: a statue's `hold` { R, L }, its items by name)
    const read = (v) => typeof v === "string" || typeof v === "number" ? value_(v, params)
      : v && typeof v === "object" && !Array.isArray(v) ? Object.fromEntries(Object.entries(v).map(([k, w]) => [k, read(w)])) : v;
    for (const [k, v] of Object.entries(def.data ?? {})) if (!k.startsWith("_")) data[k] = read(v);
    return { name, geometry: { position: new Float32Array(0), index: new Uint16Array(0) }, instances: placements(def, P, params),
             kind: "marker", role: def.role, data };
  }

  if (def.type === "column") {                     // a drum: `sides` flat faces, capped
    // a drum's sides come from the same knob: a full circle is four quarters, so 2 per 90 is an octagon
    const r = P(def.radius), h = P(def.height);
    const sides = Math.max(3, Math.round(def.sides !== undefined ? P(def.sides) : 4 * detailFor(params, r)));
    // `taper` is the top's share of the foot's radius: a shaft's entasis, a pier's batter
    const m = drum(mesh(), r, r * P(def.taper, 1), 0, h, sides);
    return { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "column" };
  }

  throw new Error(`part "${name}" has no known type (${def.type})`);
}

function baseOf(b, parts, params) {
  const P = (v, d) => num_(v ?? d, params);
  const h = P(b.height, 0.6), n = Math.max(1, Math.round(P(b.steps, 1))), out = P(b.stepOut, 0.4), margin = P(b.margin, 2);
  let pts;
  if (b.plan) pts = planPoints(planOf(b.plan, P));
  else {
    let x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9;
    for (const q of parts) {
      const p = q.geometry.position;
      for (const [yaw, X, , Z] of q.instances) {
        const c = Math.cos(yaw), s2 = Math.sin(yaw);
        for (let i = 0; i < p.length; i += 3) {
          const x = p[i] * c + p[i + 2] * s2 + X, z = -p[i] * s2 + p[i + 2] * c + Z;
          if (x < x0) x0 = x; if (x > x1) x1 = x; if (z < z0) z0 = z; if (z > z1) z1 = z;
        }
      }
    }
    const cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
    pts = planPoints({ rect: [x1 - x0 + 2 * margin, z1 - z0 + 2 * margin] }).map(([x, z]) => [x + cx, z + cz]);
  }
  // one solid, stepped: each step's outline at its foot and at its tread, the next one in by `stepOut`
  const levels = [];
  for (let i = 0; i < n; i++) {
    const o = insetPoints(pts, -out * (n - 1 - i));
    levels.push({ pts: o, y: i * h / n }, { pts: o, y: (i + 1) * h / n });
  }
  const m = stackMesh(mesh(), levels);
  for (const q of parts) q.instances = q.instances.map(([a, x, y, z]) => [a, x, y + h, z]);
  return [{ name: "base", geometry: m.arrays(), instances: [[0, 0, 0, 0]], kind: "base", top: h }];
}

// the whole definition: params, parts, and what to build
export function assemble(doc, overrides = {}) {
  // Params are resolved LAZILY, so their order in the file does not matter: "vaultSpringing": "archCrown" may
  // stand above the line that defines archCrown, which is how one writes them when the reading order follows
  // the building rather than the dependencies. A parameter defined in terms of itself is caught and named.
  // A key starting with "_" is a note, not a parameter: it lets the reason for a number sit on the line under
  // it instead of in a comment block somewhere else. Notes are dropped before anything is evaluated.
  const raw = Object.fromEntries(Object.entries(doc.params ?? {}).filter(([k]) => !k.startsWith("_")));
  // `build` is not a parameter: it says WHICH PARTS to build, and a caller may ask for some of them -- the
  // village takes a cathedral's arcades and vaults from a definition whose walls and roofs it builds itself.
  // A PART MAY SAY WHAT IT STANDS ON (`standsOn: ["neck"]`): asking for it builds that too, in the doc's own order -- a
  // caller that picks a domed tower's drum and cap cannot leave out the neck they stand on and set them in the air
  const asked = overrides.build ?? doc.build ?? [];
  const need = new Set();
  const want = (n) => { if (need.has(n)) return; need.add(n); for (const u of doc.parts?.[n]?.standsOn ?? []) want(u); };
  for (const b of asked) want(typeof b === "string" ? b : b.part);
  const order = [...(doc.build ?? []), ...Object.keys(doc.parts ?? {})];
  const build = [...asked.filter((b) => typeof b !== "string"),
                 ...[...new Set(order)].filter((n) => need.has(n) && !asked.some((b) => typeof b !== "string" && b.part === n)),
                 ...[...need].filter((n) => !order.includes(n))];
  for (const [k, v] of Object.entries(overrides)) if (v !== undefined && v !== null && k !== "build" && k !== "base" && k !== "fit") raw[k] = v;
  const params = {}, busy = new Set();
  const view = new Proxy({}, {
    has: (_, k) => k in raw,
    get: (_, k) => {
      if (k in params) return params[k];
      if (busy.has(k)) throw new Error(`the parameter "${String(k)}" is defined in terms of itself`);
      busy.add(k);
      const v = value_(raw[k], view);
      busy.delete(k);
      return (params[k] = v);
    },
  });
  for (const k of Object.keys(raw)) view[k];        // resolve them all (numbers, and the odd word)
  params.detail = detailOf(params);
  const parts = build.flatMap((b) => buildPart(typeof b === "string" ? b : b.part, doc.parts, params));
  // THE BASE: every building stands on a platform -- `base: { height, steps, stepOut, margin, plan }`. Without a
  // `plan` it is worked out from the building itself: the rectangle round everything it has built, `margin` out.
  // The platform is built first and everything else is lifted onto it, so its top IS the ground floor.
  if (doc.base && overrides.base !== false) parts.unshift(...baseOf(doc.base, parts, params));
  // RAILINGS where a stair has no wall beside it: the whole building is there now to ask
  if (doc.railing !== false) parts.push(...railingsFor(parts, doc.railing ?? {}, params));
  // THE FURNITURE GIVEN ROOM (room.js), the whole building being there: a set standing in a wall, a chimney, a column or
  // a doorway moved to the nearest place it stands clear, or left out -- `fitted` says which
  const fitted = overrides.fit === false ? [] : fitFurniture(parts);
  return { name: doc.name ?? "building", params, parts, fitted };
}
