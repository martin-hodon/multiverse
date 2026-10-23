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
import { wallFace, stepsFace, tunnelFace, extrude, straight, straightAt, radial, sweep, corridor, flank, along, mesh, domeShell, domeRibs, groinRibs, pendentives, frame, groinVault, roofMesh, roofLevels, overhang, curvedRoof, flightFace, slabFace, helix, helixAlong, staircase, drum, box, cofferedSurface, planPoints, prismMesh, stackMesh, enclosureMesh, flyerMesh, tieredWall, insetPoints, glassPanes } from "./build.js";
import { archCurve } from "./profiles.js";
import { index as solidIndex, insideOf, cellOf, heightOver } from "./solid.js";
import { fitFurniture } from "./room.js";   // the furniture given room: moved off chimneys, columns and doorways, or left out
import { domeRows, earClip } from "./build.js";
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
  for (const k of ["seg", "rise", "spread", "over", "bulge", "neck", "lobe", "bow", "waist", "lift", "lo", "hi"]) if (k in out) out[k] = num_(out[k], params);
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
                 ...(q.foot ? { foot: headOf(q.foot, params) } : {}), ...glassOf(q, params) });
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
const itemsOf = (doc) => [...new Set(Object.values(doc.parts ?? {}).map((d) => d?.type === "item" ? d.item : d?.type === "zone" ? FURNISHING.zones[d.zone]?.item : null).filter(Boolean))];
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
    return { h, openings: glazed(laidOut(t.openings, L, P, params), flagOf(t.glass, params)) };
  });
}

// ONE OPENING from its definition: centre `at`, `width`, `sill`, `springing`, its `head` and (if it has one) its
// `foot` -- the profile below the sill that makes a round window round.
const openingOf = (k, P, params) => ({
  at: P(k.at), width: P(k.width), sill: P(k.sill, 0), springing: P(k.springing ?? k.sill, 0),
  head: headOf(k.head, params), ...(k.foot ? { foot: headOf(k.foot, params) } : {}), ...glassOf(k, params) });

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
const withGlass = (part, g) => (!g || !g.counts.tris) ? part
  : [part, { name: part.name + " glass", geometry: g.arrays(), instances: part.instances, kind: "glass", shell: true }];

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
  const m = build ? domeShell(mesh(), { sides, sweep: share, turn, oculus, thickness, curve, base: 0, cap: def.cap !== false, coffers: cf }) : null;
  return { m, curve, sides, sweep: share, turn, oculus, instances: placements(def, P, params), rise: Math.max(...curve.map(([, y]) => y)) };
}

// WHERE A PART'S TOP IS: a dome's crown (its placement plus the meridian's rise), or the head of anything with a
// height -- so a finial, a lantern or a cross can stand ON something rather than at a guessed height (`atop`)
// `r`: WHERE A DOME HAS NARROWED TO THAT RADIUS -- a lantern `r` wide stands on the dome's surface there, not on its
// tip in the air (a pointed or onion dome is narrower than its lantern for its last metres)
function topOf(name, defs, params, r = 0) {
  const d = defs[name], P = (v, dd) => num_(v ?? dd, params);
  if (!d) throw new Error(`"atop": no part named "${name}"`);
  // (and if it stands `atop` another in turn, from that one's top: a ball on a roof on a lantern on a dome)
  const y0 = (placements(d, P, params)[0] ?? [0, 0, 0, 0])[2] + P(d.y, 0)
           + (d.atop ? topOf(d.atop, defs, params, d.atopR !== undefined ? P(d.atopR) : 0) : 0);
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

// A RAILING WHERE A STAIR'S SIDE IS OPEN. Every stair carries its walking path (every tread's middle, its width); along
// each side, just past the tread's edge, at knee and at chest height, the assembled building is asked whether stone
// is there -- a wall the stair hugs, the newel, the turret round a spiral. Where it is not, the side gets a railing,
// in the building's own kind (`railing: { type, height }` on the definition, a stair's own `railing` overriding it,
// `false` for none): "balusters" (a post at every tread and a handrail), "iron" (thin posts, a handrail, a middle
// rail), "stone" (a parapet, solid, sloping with the flight). A railing is its own part, "<stair> railing", in the
// building's frame -- a wall to the walk (the game's wall field reads it), a thing to lean on.
function railingsFor(parts, spec, params) {
  // (a spiral climbs inside its turret round its newel: walled both sides all the way; it gets none)
  const stairs = parts.filter((p) => p.path && p.kind !== "railing" && p.kind !== "spiral-stair" && p.railing !== false);
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
    q(ring[0][3], ring[0][2], ring[0][1], ring[0][0]); q(ring[e][0], ring[e][1], ring[e][2], ring[e][3]);
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
      for (const q of st.path) {
        const p = W(q.p), prev = cur[cur.length - 1];
        if (q.landing || (prev && (Math.hypot(p[0] - prev.p[0], p[2] - prev.p[2]) > 1.2 || Math.abs(p[1] - prev.p[1]) > .45))) {
          if (cur.length > 1) runs.push(cur); cur = q.landing ? [] : [{ p, w: q.w }];
        } else cur.push({ p, w: q.w });
      }
      if (cur.length > 1) runs.push(cur);
      for (const run of runs) {
        const n = run.map((q, i) => {
          const a = run[Math.max(0, i - 1)].p, b = run[Math.min(run.length - 1, i + 1)].p;
          let dx = b[0] - a[0], dz = b[2] - a[2]; const l = Math.hypot(dx, dz) || 1; dx /= l; dz /= l;
          return [-dz, dx];
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
      if (loop.length > 2 && loop[0] && loop[loop.length - 1] && same(loop[0].p, loop[loop.length - 1].p)) {
        const a = loop[0], b = loop.pop(), m2 = [a.out[0] + b.out[0], a.out[1] + b.out[1]], l2 = Math.hypot(...m2) || 1;
        a.out = [m2[0] / l2, m2[1] / l2]; a.corner = true;
      }
      const inset = (q) => [q.p[0] - q.out[0] * .02, q.p[1], q.p[2] - q.out[1] * .02];
      let openAt = loop.map((q) => q && openBeside(inset(q), q.out, .02));
      const cut = openAt.findIndex((v) => !v);
      if (cut > 0) { loop.push(...loop.splice(0, cut)); openAt = [...openAt.slice(cut), ...openAt.slice(0, cut)]; }
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
export function buildPart(name, defs, params) {
  if (defs[name]?.when !== undefined && !passes(defs[name].when, params)) return [];
  const def = defs[name];
  if (def && def.atop) {
    // `atop`: stand on another part's top -- every placement's height is measured from there
    // (`atopR`: its own radius -- it stands where the dome has narrowed to that; its placement's y then sinks it in)
    const lift = topOf(def.atop, defs, params, def.atopR !== undefined ? num_(def.atopR, params) : 0);
    const out = buildPart(name, { ...defs, [name]: { ...def, atop: undefined, atopR: undefined } }, params);
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
      const g = mesh();
      const m = tieredWall(mesh(), w, tiersOf(def.tiers, P(def.height), w, P, params).map((t) => ({ ...t, openings: glazed(t.openings, flagOf(def.glass, params)) })),
                           (y0) => straightAt(P(def.thickness), def.center === false ? 0 : -w / 2, y0), { glass: g });
      return withGlass({ name, geometry: m.arrays(), instances: placements(def, P, params), kind: "wall", bayWidth: w }, g);
    }
    const face = wallFace(w, P(def.height), openings);
    // WHERE IT STANDS. A round building needs no placement -- a ring IS its placement -- but a straight one is
    // nothing without it: a nave is two arcades a nave's width apart, and its transept is the same wall turned
    // a right angle. `at`: [x, y, z, yaw] per copy, as a column's. `center` measures the wall from its middle
    // rather than its corner, which is how one writes a symmetrical building without arithmetic in every line.
    const map = straightAt(P(def.thickness), def.center === false ? 0 : -w / 2);
    const m = extrude(face, map);
    return withGlass({ name, geometry: m.arrays(), instances: placements(def, P, params),
             face, kind: "wall", bayWidth: w }, glassPanes(face, map, mesh()));
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
    const n = Math.max(3, Math.round(P(def.count)));
    const rOuter = P(def.rOuter), rInner = P(def.rInner);
    const w = 2 * Math.PI * rOuter / n;            // the bay's width AT THE OUTER FACE: the ring closes exactly
    // `solid: true` (or no opening at all) is a blind ring: the cavea's substructure is a mass of masonry with
    // the podium wall as its inner face, not an arcade.
    const opening = def.opening ?? {};
    const openings = (def.solid || def.opening === null) ? [] : [
      { ...openingOf({ ...opening, width: opening.width ?? w * .55, at: 0 }, P, params), at: w / 2 }].map((o) => glazed([o], flagOf(def.glass, params))[0]);
    const face = wallFace(w, P(def.height), openings);
    const rmap = radial(rOuter, rInner, w), m = extrude(face, rmap);
    // [y-rotation, x, y, z] per instance: the bay is built in its own wedge, so the ring is rotations of it
    const t = turnOf(def, n, P);
    // `place` puts the whole ring somewhere (a cathedral's three tribunes stand on three sides of its octagon,
    // not at the origin); without it a ring is its own placement, at the middle of the world. It is NOT `at`:
    // on a ring that already names which BAYS are the part's own.
    // ...and `repeat` stacks it, as it does a straight part: the storeys of a round tower
    const seats = placements({ place: def.place ?? [[0, 0, 0, 0]], repeat: def.repeat }, P, params);
    const instances = seats.flatMap(([yaw, x, y, z]) => baysFor({ ...def, _name: name }, n, P)
      .map((k) => [k * 2 * Math.PI / n + t + yaw, x, y + P(def.y, 0), z]));
    return withGlass({ name, geometry: m.arrays(), instances, face, kind: "ring", bayWidth: w, count: n }, glassPanes(face, rmap, mesh()));
  }

  if (def.type === "vault") {
    // A ring of barrel vaults over the corridor between two walls -- what an arena's ambulatory is roofed
    // with. One bay's wedge is the vault's cross-section swept between its two radial planes, and the
    // cross-section is a wall face whose single opening spans the whole width: the solid left over is the
    // vault's own masonry, and the void under it is the corridor. Its extrados is flat at `top`, which is the
    // floor of the storey above.
    const n = Math.max(3, Math.round(P(def.count)));
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
    const instances = baysFor({ ...def, _name: name }, n, P).map((k) => [k * 2 * Math.PI / n + t, 0, P(def.y, 0), 0]);
    return { name, geometry: m.arrays(), instances, face, kind: "vault", count: n,
             bayWidth: 2 * Math.PI * rOut / n };
  }

  if (def.type === "steps") {
    // Seating, or a flight of stairs -- the same part at different scales. It is a stepped cross-section swept
    // through a bay's wedge, standing on `base` (the vaults' flat extrados) and rising outward with the cavea.
    // `every`/`offset` say which bays get it: leave every fifth bay out and those gaps are the vomitoria, with
    // a narrower, finer-stepped flight of the same part climbing in them.
    const n = Math.max(3, Math.round(P(def.count)));
    const rIn = P(def.rInner), rOut = P(def.rOuter), run = P(def.run);
    const base = P(def.base, 0);
    // How many steps: for a flight that runs radially, as many as fit between the two radii; for one that
    // climbs ALONG the ring the radii are its corridor, not its length, so the rise says how many there are.
    const cols = Math.max(1, (def.plan === "along")
      ? Math.round(def.steps !== undefined ? P(def.steps) : (P(def.top) - base) / P(def.rise))
      : Math.floor((rOut - rIn) / run + 1e-9));
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
    const stepOpts = { base: 0, rising: def.rising ?? "out", ...(first !== undefined ? { first } : {}) };
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
    const n = Math.max(3, Math.round(P(def.count)));
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
             ...(share < 1 ? { cut: curve.filter(([x]) => x >= -1e-9) } : {}) };
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
    const W = P(def.width) / 2, L = P(def.length) / 2, n = Math.round(P(def.steps, 3)), h = P(def.stepH, .3), o = P(def.stepOut, .35), bt = P(def.batter, 0);
    const levels = [];
    for (let i = 0; i < n; i++) {
      const e = o * (n - 1 - i);
      levels.push({ x0: -W - e - bt, x1: W + e + bt, z0: -L - e - bt, z1: L + e + bt, y: i * h }, { x0: -W - e, x1: W + e, z0: -L - e, z1: L + e, y: (i + 1) * h });
    }
    return { name, geometry: roofMesh(mesh(), levels).arrays(), instances: placements(def, P, params), kind: "crepidoma", top: n * h };
  }

  if (def.type === "roof") {
    // A ROOF: `form` (gable, hip, mansard, ... see build.js roofLevels) over a `width` x `length` plan, the
    // ridge along the length, `y` 0 where it meets the wall plane and `overhang` carrying the eave out past it.
    const a = P(def.width) / 2, b = P(def.length) / 2;
    const opt = { a, b };
    for (const k of ["pitch", "thickness", "lowerPitch", "breakH", "clip", "hipH", "ridge"]) if (def[k] !== undefined) opt[k] = P(def[k]);
    const lv0 = roofLevels(wordOf(def.form ?? "gable", params), opt), levels = overhang(lv0, P(def.overhang, 0));
    // `shell`: a covering that thick over an open roof space (a loft, an attic) instead of a roof solid down to its eaves --
    // the underside follows the slopes, the gables stand in the wall plane (build.js roofMesh)
    const inner = def.shell !== undefined ? overhang(lv0, P(def.overhang, 0), false).map((L) => ({ ...L, y: L.y - P(def.shell) })) : null;
    // A CHINESE ROOF (build.js curvedRoof) when it says how its slopes bend (`lo`, `hi`: the jujia slopes at the eave
    // and at the ridge, as a profile's) or that its corners turn up (`upturn`, `flare`, over `reach` metres)
    const chinese = ["lo", "hi", "upturn", "flare"].some((k) => def[k] !== undefined);
    const m = chinese ? curvedRoof(mesh(), levels, { lo: P(def.lo, .35), hi: P(def.hi, 1.2), steps: Math.round(P(def.steps, 2 * detailOf(params) + 2)),
                                                     upturn: P(def.upturn, 0), flare: P(def.flare, 0), reach: def.reach !== undefined ? P(def.reach) : undefined,
                                                     perSide: Math.round(P(def.perSide, Math.max(4, 2 * detailOf(params)))) })
                      : roofMesh(mesh(), levels, inner, wordOf(def.open, params) ?? null);
    return { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "roof", ridge: levels[levels.length - 1].y };
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
    return { name, geometry: m.arrays(), instances: placements(def, P, params),
             face, kind: "flight", steps, rise, run, soffit: soff, topOf: top, ...(def.walk === false ? {} : { path, edges, foot: [-.5, base, -width / 2], approach: { x0: -Math.min(width, 2), x1: 0, z0: -width, z1: 0, y: base } }) };
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
    if (landing > 0) path.push({ p: mid(n * run + landing / 2, top), w: far(n * run) - near(n * run), landing: true });
    const foot = mid(-.5, 0);
    const instances = placements(def, P, params);
    const stair = { name, geometry: m.arrays(), instances, kind: "spiral-stair", steps: n, rise, run, topOf: top, shell: post, path, foot };
    if (!post) return stair;
    const pm = drum(mesh(), r0, r0, -soffit, top + P(def.postAbove, 1), 4 * detailOf(params));
    return [stair, { name: name + " newel", geometry: pm.arrays(), instances, kind: "column", stairPart: name }];
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
    const { m, flights, path, edges } = staircase(mesh(), ends(node(def)), { run, rise, soffit });
    return { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "staircase",
             topOf: Math.max(...flights.map((f) => f.top)), flights: flights.length, path, edges, foot: flights[0].foot };
  }

  if (def.type === "box") {
    // A BLOCK: `width` (x) by `length` (z) by `height`, standing on its placement, centred on it -- a podium, a
    // course of a stylobate, a pier, the straight run of an entablature.
    const w = P(def.width), l = P(def.length), h = P(def.height);
    return { name, geometry: box(mesh(), -w / 2, w / 2, 0, h, -l / 2, l / 2).arrays(), instances: placements(def, P, params), kind: "box" };
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
    let local, stepA = 0, R = 0, spacing = 0;
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
    const add = (suffix, m, kind = "pyramid") => { const a = m.arrays(); if (a.index.length) parts.push({ name: `${name} ${suffix}`, geometry: a, instances: at, kind }); };
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

  if (def.type === "prism") {
    // A PRISM on a plan (build.js planPoints: `rect`, `chamfer`, `sides` + `radius`, or `points`), `height` tall:
    // a plinth, a platform, the solid core of a tower
    const pts = planPoints(planOf(def.plan, P));
    return { name, geometry: prismMesh(mesh(), pts, 0, P(def.height)).arrays(), instances: placements(def, P, params), kind: "prism" };
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
      return tiersOf(spec, h, L, P, params).map((t) => ({ ...t, openings: glazed(t.openings, flagOf(def.glass, params)) }));
    });
    const g = mesh();
    return withGlass({ name, geometry: enclosureMesh(mesh(), pts, t, faces, g).arrays(), instances: placements(def, P, params), kind: "enclosure" }, g);
  }

  if (def.type === "flyer") {
    // A FLYING BUTTRESS: across `span` from the pier (at the placement) to the wall it props, its soffit a rampant
    // quarter-arch from `low` at the pier to `high` at the wall, its back straight from `top0` to `top1`, `width`
    // thick. Turned by its yaw so it reaches along +x.
    const m = flyerMesh(mesh(), { span: P(def.span), low: P(def.low), high: P(def.high), top0: P(def.top0), top1: P(def.top1),
                                  width: P(def.width), per90: detailOf(params) });
    return { name, geometry: m.arrays(), instances: placements(def, P, params), kind: "flyer" };
  }

  if (def.type === "court") {
    // A RING OF ROOMS ROUND A COURTYARD -- a cloister, a palace's quadrangle, a castle's court -- as ONE thing, so its
    // floor plan is connected all the way round: outer walls on `plan` (rect, sides + radius, points), courtyard walls
    // `depth` in, `storeys` of `storeyH`, a window every `axis` metres on every face, a row of doors from the court
    // into the rooms, continuous floors on every storey, a dog-leg stair up every storey on side `stairFace`
    // (the floors cut round it), a GATE through both walls on side `gate.face` into the court, and a roof over every
    // side (`roof.form`, `roof.pitch`). It is made of the engine's own parts -- enclosures, prisms, a staircase, roofs
    // -- written here and built as any other part, and named "<court>/<part>".
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
        : { pattern: String(k), width: w, gap: axis - w, sill: sl, springing: sl + h, head, ...extra };
    };
    // (the gate's head is its own -- round unless it says -- and its springing is worked so its crown is `height`, within
    //  the ground storey)
    const gateOf = (i) => gate && gate.face === i ? { middle: { width: gate.width, sill: 0, head: gate.head, glass: false,
      springing: gate.height - archCurve(gate.width / 2, headOf(gate.head, params)).reduce((m, [, y]) => Math.max(m, y), 0) } } : {};
    const tiers = (L, i, ground) => Array.from({ length: N }, (_, k) => ({ ...(k < N - 1 ? { h: H } : {}),
      openings: k === 0 ? ground(L, i) : row(L, winW, sill, winH) }));
    // JOINS: where another building stands against an outer face (`face`, `at` from its middle, `width` along it) the
    // face has no windows -- they would look into its wall -- and, with `door`, a doorway through on the ground storey:
    // the way from the court's rooms into it (a church's crossing against the cloister's wing)
    const joins = (def.joins ?? []).map((j) => ({ face: Math.round(P(j.face)), at: P(j.at, 0), width: P(j.width),
      door: j.door ? { width: P(j.door.width, 2.4), height: P(j.door.height, 3.4), head: j.door.head ?? { profile: "semicircular" } } : null }));
    const joinedTiers = (L, i) => {
      const js = joins.filter((j) => j.face === i);
      const k = Math.floor(L / axis - .5), at = Array.from({ length: Math.max(0, k) }, (_, q) => (q - (k - 1) / 2) * axis)
        .filter((x) => js.every((j) => Math.abs(x - j.at) > j.width / 2 + winW / 2 + .3));
      const wins = at.map((x) => ({ at: x, width: winW, sill, springing: sill + winH, head }));
      const doors = js.filter((j) => j.door).map((j) => ({ at: j.at, width: j.door.width, sill: 0, glass: false, head: j.door.head,
        springing: j.door.height - archCurve(j.door.width / 2, headOf(j.door.head, params)).reduce((m, [, y]) => Math.max(m, y), 0) }));
      return Array.from({ length: N }, (_, q) => ({ ...(q < N - 1 ? { h: H } : {}), openings: q === 0 ? [...wins, ...doors] : wins }));
    };
    const defs = {};
    defs["outer walls"] = { type: "enclosure", plan: { points: O }, thickness: t, height: N * H, ...(def.glass !== undefined ? { glass: def.glass } : {}),   // (glazed or not: the court's say)
      faces: Object.fromEntries(O.map((p, i) => [i, joins.some((j) => j.face === i) ? joinedTiers(len(p, O[(i + 1) % n]), i)
                                                   : tiers(len(p, O[(i + 1) % n]), i, (L, j) => row(L, winW, sill, winH, gateOf(j)))])) };
    defs["court walls"] = { type: "enclosure", plan: { points: courtLine }, thickness: t, height: N * H, ...(def.glass !== undefined ? { glass: def.glass } : {}),
      faces: Object.fromEntries(courtLine.map((p, i) => [i, tiers(len(p, courtLine[(i + 1) % n]), i,
        (L, j) => row(L, doorW, 0, doorH - doorW / 2, gateOf(j)))])) };
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
    // a roof over every side, along its outer edge
    O.forEach((p, i) => {
      const q = O[(i + 1) % n], L = len(p, q), ex = (q[0] - p[0]) / L, ez = (q[1] - p[1]) / L;
      let mx = -ez, mz = ex;
      const ci = court[i];
      if ((ci[0] - p[0]) * mx + (ci[1] - p[1]) * mz < 0) { mx = ez; mz = -ex; }
      defs[`roof ${i + 1}`] = { type: "roof", form: wordOf(def.roof?.form ?? "hip", params), width: D, length: L, pitch: P(def.roof?.pitch, 40),
        overhang: P(def.roof?.overhang, .4), at: [[(p[0] + q[0]) / 2 + mx * D / 2, N * H, (p[1] + q[1]) / 2 + mz * D / 2, Math.atan2(ex, ez)]] };
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
    const given = {};
    for (const [k, v] of Object.entries(def.params ?? {})) if (!k.startsWith("_")) given[k] = value_(v, params);
    const ref = { path: def.item, seed: def.seed !== undefined ? P(def.seed) : 1, params: given, materials: def.materials ?? null };
    const it = itemOf(ref), places = placements(def, P, params), [lo, hi] = [it.bounds.lo, it.bounds.hi];
    const keep = def.markers ?? true, more = {};
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
    for (const [k, v] of Object.entries(def.data ?? {})) if (!k.startsWith("_")) data[k] = typeof v === "string" || typeof v === "number" ? value_(v, params) : v;
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
