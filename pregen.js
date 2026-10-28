// PREGENERATED DATA: what startup would otherwise work out from scratch, read from pregen/ instead.
//
// Most of a world's startup is three things, every one of them a pure function of data that rarely changes
// (measured, docs/pregen.md): the pattern TILES of the buildings' finishes and of the people's fabrics (a marble's
// veins and a plaster's clouds are noise per texel), the finished building GEOMETRY (every surface cut and told
// inside from outside by the building's interiors), and the walk's WALL FIELDS. `python3 build/pregen.py` builds them all once, in a
// headless browser through the very same code, and writes them into pregen/; the game fetches the ones its world
// needs and uses them instead of computing them.
//
// NOTHING IS TRUSTED BY NAME. Every entry is filed under a HASH of what it was made from -- a tile under its
// pattern (and every pattern it uses), palette, params and resolution; a building's geometry under its assembly's
// actual triangles and instances, its finish and the sizes of the patterns the finish names; a wall field under the
// assembly and the cell -- and under the source of the code that makes them (the manifest lists the files, and the
// game hashes them when it can fetch them). Edit a building, a finish, a pattern or that code and the entry simply
// is not found: the game makes it from scratch as it always did. A missing pregen/ folder is the same.
import { patternOf, paletteOf, sizeOf, LAYER_KINDS } from "./patterns.js";

export const PREGEN_BASE = new URL("./pregen/", import.meta.url).href;
// THE SECTIONS, each checked against the code that makes IT (2026-10-06): an edit to architecture.js retires the
// buildings' geometry and wall fields, not every tile; an edit to the face's code, the faces -- one list for the whole
// cache meant a line changed anywhere sent every start back to drawing everything
export const SECTIONS = {
  tiles: ["pregen.js", "patterns.js", "expr.js", "fabric.js", "glyphs.js", "murals.js"],          // pattern tiles, fabrics
  buildings: ["pregen.js", "architecture.js", "arch/finish.js", "arch/solid.js", "patterns.js", "expr.js"],   // finished geometry, wall fields
  faces: ["pregen.js", "heads.js", "items.js", "face.js", "hair.js", "thorns.js", "jewelry.js", "petals.js", "defs.js", "expr.js"],   // heads with their hair and what is worn on them
  wings: ["pregen.js", "butterflies.js"],                                                       // the butterflies' painted wings
  maps: ["pregen.js", "terrain_lab.js"],                                                        // the grown lands (mapgen.js), by seed
};
export const PREGEN_SOURCES = [...new Set(Object.values(SECTIONS).flat())];
// what the game has fetched, by key -- and, while build/pregen.py runs, what it is recording. `ok`: the sections in
// play; `faceIndex` the faces the cache has (key -> { file, family }), `faceFamilies` family -> keys
export const PREGEN = { tiles: new Map(), fabrics: new Map(), groups: new Map(), walls: new Map(), wings: new Map(), faceIndex: null, faceFamilies: new Map(),
                        ok: {}, manifest: null, record: null, active: false, misses: [] };
// what the game had to make after all (pregen/ in play but without it): said once a second, so a stale cache is seen
// -- but not the town's buildings (town.js), which the world's seed lays out: they are made at startup by design
const PER_WORLD = /^(village\/|town$)/;
const SECTION_OF = { tile: "tiles", fabric: "tiles", geometry: "buildings", walls: "buildings", face: "faces", wing: "wings", map: "maps" };
export function pregenMiss(kind, what, key) {
  if (!PREGEN.active || PER_WORLD.test(what) || PREGEN.ok[SECTION_OF[kind]] === false) return;   // (a stale section: said once already)
  PREGEN.misses.push(`${kind} ${what} (${key})`);
  if (PREGEN.misses.length === 1) setTimeout(() => { console.info(`pregen/: made from scratch after all -- ${PREGEN.misses.length}: ${PREGEN.misses.slice(0, 12).join("; ")}`); PREGEN.misses.length = 0; }, 1000);
}

// ---- hashing: FNV-1a in two 32-bit lanes (a 64-bit key), over strings, numbers and typed arrays -------------------
export function hasher() {
  let a = 0x811c9dc5, b = 0x9e3779b9;
  const word = (w) => { a = Math.imul(a ^ w, 16777619); b = Math.imul(b ^ (w + 0x7f4a7c15), 2246822519); b ^= b >>> 15; };
  const h = {
    str(s) { for (let i = 0; i < s.length; i++) word(s.charCodeAt(i)); word(0x2f); return h; },
    arr(t) {
      word(t.length);
      const u8 = new Uint8Array(t.buffer, t.byteOffset, t.byteLength);
      if (t.byteOffset % 4 === 0) { const u32 = new Uint32Array(t.buffer, t.byteOffset, t.byteLength >> 2); for (let i = 0; i < u32.length; i++) word(u32[i]); }
      else for (let i = 0; i < (t.byteLength & ~3); i++) word(u8[i]);
      for (let i = t.byteLength & ~3; i < t.byteLength; i++) word(u8[i]);
      return h;
    },
    json(v) { return h.str(JSON.stringify(v, (k, x) => (ArrayBuffer.isView(x) ? `#${hasher().arr(x).hex()}` : typeof x === "function" ? undefined : x))); },
    hex() { return (a >>> 0).toString(16).padStart(8, "0") + (b >>> 0).toString(16).padStart(8, "0"); },
  };
  return h;
}

// ---- the keys ---------------------------------------------------------------------------------------------------
// a pattern and every pattern it USES, as data (a carpet is its border's pattern round its field's)
function closure(ref, out = {}) {
  if (out[ref]) return out;
  const def = patternOf(ref);
  out[ref] = def ?? null;
  const walk = (ls) => { for (const l of ls ?? []) { if (l.use) closure(l.use, out); if (l.kind) out["@" + l.kind + ":" + ref] = LAYER_KINDS[l.kind]?.deps?.(l) ?? null; walk(l.layers); } };
  walk(def?.layers);
  return out;
}
export const tileKey = (pattern, palette, params, res) =>
  hasher().str("tile").json({ c: closure(pattern), pal: paletteOf(patternOf(pattern), palette), params, res: res ?? null }).hex();
export const fabricKey = (ref, res) => hasher().str("fabric").json({ c: closure(ref), res }).hex();
// an assembly, as the triangles and instances it IS (whatever definitions and components made it)
const asmHashes = new WeakMap();
export function asmHash(asm) {
  let k = asmHashes.get(asm);
  if (k) return k;
  const h = hasher().str("asm");
  for (const p of asm.parts) {
    const { geometry, ...rest } = p;
    h.json(rest);
    for (const [name, arr] of Object.entries(geometry ?? {})) if (ArrayBuffer.isView(arr)) h.str(name).arr(arr);
  }
  asmHashes.set(asm, k = h.hex());
  return k;
}
export const groupsKey = (asm, finish, sizeOf) => hasher().str("groups").str(asmHash(asm)).json(finish)
  .json((finish.rules ?? []).map((r) => (r.pattern ? sizeOf(r) : null))).hex();
export const wallsKey = (asm, cell) => hasher().str("walls").str(asmHash(asm)).json(cell).hex();
// is the cache in play at all (a manifest found, or the generator recording)? -- else nobody pays for the hashing
export const pregenOn = () => PREGEN.active || !!PREGEN.record;

// ---- the game: the manifest, and the entries a world needs --------------------------------------------------------
const hexOf = (h) => hasher().str(h).hex();
async function codeHash(sources) {
  const texts = await Promise.all(sources.map(async (f) => { const r = await fetch(new URL("./" + f, import.meta.url)); if (!r.ok) throw new Error(f); return r.text(); }));
  const h = hasher(); for (const t of texts) h.str(t);
  return h.hex();
}
// fetch the manifest (none: nothing happens) and, for the buildings named (keys of architecture.js BUILDINGS), their
// geometry, wall fields and tiles -- and every fabric -- into memory, before the world is built from them
// THE EARLY PART, as this module is imported (below): the manifest, the sections' code, every fabric, the wings, the
// list of faces -- people are made while the modules load (species.js builds its winged people and centaurs), and their
// cloth was drawn from scratch before loadPregen came
let EARLY = null;
async function loadEarly() {
  let m;
  try { const r = await fetch(PREGEN_BASE + "manifest.json", { cache: "no-store" }); if (!r.ok) return null; m = await r.json(); } catch { return null; }
  // (the code that made each section: when the sources can be read -- the dev setup -- they must be what made it; a
  //  manifest from before the sections has one hash for all)
  const secs = m.sections ?? Object.fromEntries(Object.keys(SECTIONS).map((s) => [s, { code: m.code, sources: m.sources ?? PREGEN_SOURCES }]));
  const stale = [];
  for (const s of Object.keys(SECTIONS)) {
    if (!secs[s]) { PREGEN.ok[s] = false; continue; }
    try { PREGEN.ok[s] = (await codeHash(secs[s].sources)) === secs[s].code; } catch { PREGEN.ok[s] = true; }   // (a distribution without the sources: take it as built)
    if (!PREGEN.ok[s]) stale.push(s);
  }
  if (stale.length) console.info(`pregen/: ${stale.join(", ")} made by other code -- run build/pregen.py; ${stale.length === Object.keys(SECTIONS).length ? "building from scratch" : "those made from scratch"}`);
  if (!Object.values(PREGEN.ok).some(Boolean)) return null;
  PREGEN.manifest = m; PREGEN.active = true;
  const jobs = [];
  if (PREGEN.ok.tiles) for (const [k, f] of Object.entries(m.fabrics ?? {})) jobs.push(readImage(f).then((c) => PREGEN.fabrics.set(k, c)));
  if (PREGEN.ok.wings) for (const [k, f] of Object.entries(m.wings ?? {})) jobs.push(readImage(f).then((c) => PREGEN.wings.set(k, c)));
  // (the faces are only listed here: each is fetched when a head first needs it -- heads.js)
  if (PREGEN.ok.faces && m.faces) {
    PREGEN.faceIndex = m.faces;
    for (const [k, e] of Object.entries(m.faces)) { if (!PREGEN.faceFamilies.has(e.family)) PREGEN.faceFamilies.set(e.family, []); PREGEN.faceFamilies.get(e.family).push(k); }
  }
  const res = await Promise.allSettled(jobs);
  return { m, bad: res.filter((r) => r.status === "rejected").length };
}
// THE BUILDINGS' PART: for the buildings named (keys of architecture.js BUILDINGS, and "items", "world"), their geometry,
// wall fields and tiles, into memory before the world is built from them
export async function loadPregen(buildings = []) {
  const e0 = await EARLY;
  if (!e0) return false;
  const m = e0.m, t0 = performance.now(), jobs = [];
  const want = new Set();
  for (const b of buildings) {
    const e = m.buildings?.[b];
    if (!e) continue;
    if (PREGEN.ok.buildings) {
      for (const [k, f] of Object.entries(e.groups ?? {})) jobs.push(readBin(f).then((buf) => PREGEN.groups.set(k, unpackGroups(buf))));
      for (const [k, f] of Object.entries(e.walls ?? {})) jobs.push(readBin(f).then((buf) => PREGEN.walls.set(k, unpackWalls(buf))));
    }
    for (const k of e.tiles ?? []) want.add(k);
  }
  if (PREGEN.ok.tiles) for (const k of want) if (m.tiles?.[k] && !PREGEN.tiles.has(k)) jobs.push(readImage(m.tiles[k]).then((c) => PREGEN.tiles.set(k, c)));
  const res = await Promise.allSettled(jobs);
  const bad = e0.bad + res.filter((r) => r.status === "rejected").length;
  console.info(`pregen/: ${PREGEN.groups.size} buildings' geometry, ${PREGEN.walls.size} wall fields, ${PREGEN.tiles.size} tiles, ${PREGEN.fabrics.size} fabrics, ${PREGEN.wings.size} butterflies' wings, ${Object.keys(PREGEN.faceIndex ?? {}).length} faces listed in ${(performance.now() - t0).toFixed(0)}ms${bad ? ` (${bad} files missing)` : ""}`);
  return true;
}
// A GROWN LAND (mapgen.js): the terrain lab's fields after its ages, by the seed and the growing's own numbers
export const mapKey = (o) => hasher().str("map").json(o).hex();
export const packMap = (g) => pack({ stats: g.stats, dx: g.dx, inlet: g.inlet }, [g.H, g.W, g.Q]);
export async function fetchMap(key) {
  const { head, arrays: [H, W, Q] } = unpack(await readBin(PREGEN.manifest.maps[key].file));
  return { ...head, H, W, Q };
}
// the seeds whose land (and, recorded, whose town) the cache has: index.html picks a world among them when no ?seed is asked
export const cachedSeeds = () => PREGEN.ok.maps ? [...new Set(Object.values(PREGEN.manifest?.maps ?? {}).map((e) => e.seed))] : [];
// A FACE from the cache (heads.js): its item's groups as built -- fetched when a head first needs it
export async function fetchFace(key) {
  const e = PREGEN.faceIndex?.[key];
  if (!e) throw new Error("no face " + key);
  return unpackFace(await readBin(e.file));
}
async function readBin(file) {
  const r = await fetch(PREGEN_BASE + file);
  if (!r.ok) throw new Error(file);
  return new Response(r.body.pipeThrough(new DecompressionStream("gzip"))).arrayBuffer();
}
// an image, drawn into a canvas exactly as the pattern code would have drawn it (no colour management, no premultiply)
async function readImage(file) {
  const r = await fetch(PREGEN_BASE + file);
  if (!r.ok) throw new Error(file);
  const bmp = await createImageBitmap(await r.blob(), { premultiplyAlpha: "none", colorSpaceConversion: "none" });
  const cv = typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(bmp.width, bmp.height) : Object.assign(document.createElement("canvas"), { width: bmp.width, height: bmp.height });
  cv.getContext("2d", { willReadFrequently: true }).drawImage(bmp, 0, 0);
  return cv;
}

// ---- the binary files ---------------------------------------------------------------------------------------------
// a building's finished groups (arch/finish.js): a JSON header -- per group its rule (an index into the finish's rules),
// whether it is glass, and how long its arrays are -- then the arrays, Float32, one after the other
export function packGroups(groups, finish) {
  const head = groups.map((g) => ({ rule: g.rule ? finish.rules.indexOf(g.rule) : -1, glass: !!g.glass, pos: g.pos.length, nor: g.nor.length, uv: g.uv?.length ?? 0, parts: g.parts ? [...g.parts] : undefined }));
  return pack(head, groups.flatMap((g) => [g.pos, g.nor, ...(g.uv ? [g.uv] : [])]));
}
export function unpackGroups(buf) {
  const { head, arrays } = unpack(buf);
  let i = 0;
  return head.map((h) => ({ rule: h.rule, glass: h.glass, pos: arrays[i++], nor: arrays[i++], uv: h.uv ? arrays[i++] : null, parts: h.parts ? new Map(h.parts) : undefined }));
}
// a FACE (heads.js): an item's groups as buildItem made them -- each its material and roles, then its arrays (indexed:
// a head is a few thousand triangles over fewer vertices); the item's name and bounds
export function packFace(built) {
  const head = { name: built.name, bounds: built.bounds, groups: built.groups.map((g) => ({ material: g.material, roles: [...(g.roles ?? [])] })) };
  return pack(head, built.groups.flatMap((g) => [new Float32Array(g.pos), new Float32Array(g.nor), new Float32Array(g.uv), new Uint32Array(g.idx)]));
}
export function unpackFace(buf) {
  const { head, arrays } = unpack(buf);
  let i = 0;
  return { name: head.name, bounds: head.bounds, markers: [], guides: [], params: {},
           groups: head.groups.map((g) => ({ material: g.material, roles: new Set(g.roles), pos: arrays[i++], nor: arrays[i++], uv: arrays[i++], idx: arrays[i++] })) };
}
// a wall field: its cells' keys, how many height intervals each has, and the intervals
export function packWalls(cells) {
  const keys = [...cells.keys()], counts = keys.map((k) => cells.get(k).length);
  const iv = new Float32Array(counts.reduce((a, b) => a + b, 0) * 2);
  let o = 0; for (const k of keys) for (const [y0, y1] of cells.get(k)) { iv[o++] = y0; iv[o++] = y1; }
  return pack({ n: keys.length }, [new Float64Array(keys), new Float32Array(counts), iv]);
}
export function unpackWalls(buf) {
  const { arrays: [keys, counts, iv] } = unpack(buf);
  const cells = new Map();
  let o = 0;
  for (let i = 0; i < keys.length; i++) { const list = []; for (let c = 0; c < counts[i]; c++, o += 2) list.push([iv[o], iv[o + 1]]); cells.set(keys[i], list); }
  return cells;
}
// (the container: header length, the header as JSON, each array's type and length, the arrays 8-aligned)
function pack(head, arrays) {
  const meta = new TextEncoder().encode(JSON.stringify({ head, types: arrays.map((a) => [a.constructor.name, a.length]) }));
  let size = 8 + meta.length; size = Math.ceil(size / 8) * 8;
  const offs = arrays.map((a) => { const o = size; size = Math.ceil((size + a.byteLength) / 8) * 8; return o; });
  const buf = new ArrayBuffer(size), dv = new DataView(buf);
  dv.setUint32(0, meta.length, true);
  new Uint8Array(buf, 8, meta.length).set(meta);
  arrays.forEach((a, i) => new Uint8Array(buf, offs[i], a.byteLength).set(new Uint8Array(a.buffer, a.byteOffset, a.byteLength)));
  return buf;
}
function unpack(buf) {
  const n = new DataView(buf).getUint32(0, true);
  const { head, types } = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 8, n)));
  let o = Math.ceil((8 + n) / 8) * 8;
  const T = { Float32Array, Float64Array, Uint32Array, Uint16Array, Int32Array };
  const arrays = types.map(([t, len]) => { const C = T[t]; const a = new C(buf, o, len); o = Math.ceil((o + a.byteLength) / 8) * 8; return a; });
  return { head, arrays };
}

// ---- the generator (build/pregen.py drives pregen.html) -----------------------------------------------------------
// while recording, every tile, fabric, building's groups and wall field made is kept (with the building it was made
// for, so the game can fetch a building's files by its name); pregen.html writes them out
export function startRecording() {
  PREGEN.record = { current: null, tiles: new Map(), fabrics: new Map(), groups: new Map(), walls: new Map(), wings: new Map(), faces: new Map(), maps: new Map(), buildings: {} };
  return PREGEN.record;
}
export function recordFor(kind, key, value) {
  const R = PREGEN.record;
  if (!R) return;
  if (value !== null || !R[kind].has(key)) R[kind].set(key, value);   // (null: only noting which building uses it)
  if (R.current && (kind === "tiles" || kind === "groups" || kind === "walls")) {
    const b = (R.buildings[R.current] ??= { groups: [], walls: [], tiles: [] });
    if (!b[kind].includes(key)) b[kind].push(key);
  }
}
export { codeHash, hexOf };

// ---- A WORLD RECORDING (build/pregen.py's second pass: index.html?pregenrecord) -----------------------------------
// The game builds a world as it always does, and everything it had to make that the cache has not got -- the tiles of
// its seeded furniture, carts and tools, the faces of families the generator's random people missed -- is kept and
// written out as a fragment, which pregen.py merges into the manifest (under "world": every tile a world used).
// Random worlds: each run of the generator keeps another lot.
const HERE = typeof location !== "undefined" ? location : null;
export const RECORD_WORLD = !!HERE && new URLSearchParams(HERE.search).has("pregenrecord");
if (RECORD_WORLD) { startRecording(); PREGEN.record.world = true; PREGEN.record.current = "world"; }
export async function flushWorld() {
  const R = PREGEN.record, m = PREGEN.manifest ?? {};
  const put = (path, body) => fetch(PREGEN_BASE + path, { method: "POST", body }).then((r) => { if (!r.ok) throw new Error(`${path}: ${r.status}`); });
  const png = (cv) => (cv.convertToBlob ? cv.convertToBlob({ type: "image/png" }) : new Promise((ok) => cv.toBlob(ok, "image/png")));
  const gzip = (buf) => new Response(new Blob([buf]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer();
  const frag = { tiles: {}, wings: {}, faces: {}, maps: {}, buildings: {}, used: [] };
  for (const [k, cv] of R.tiles) { frag.used.push(k); if (cv && !m.tiles?.[k]) { const f = `tiles/${k}.png`; await put(f, await png(cv)); frag.tiles[k] = f; } }
  for (const [k, e] of R.maps) { const f = `maps/${k}.bin`; await put(f, await gzip(e.buf)); frag.maps[k] = { file: f, seed: e.seed }; }
  // (the world's own town: its houses' finished geometry and wall fields, under "world/<seed>" -- index.html asks for its own)
  for (const [name, b] of Object.entries(R.buildings)) {
    if (!name.startsWith("world/")) continue;
    const e = { groups: {}, walls: {}, tiles: b.tiles };
    for (const k of b.groups) if (R.groups.get(k)) { const f = `buildings/${k}.bin`; await put(f, await gzip(R.groups.get(k))); e.groups[k] = f; }
    for (const k of b.walls) if (R.walls.get(k)) { const f = `fields/${k}.bin`; await put(f, await gzip(R.walls.get(k))); e.walls[k] = f; }
    frag.buildings[name] = e;
  }
  for (const [k, cv] of R.wings) if (cv && !m.wings?.[k]) { const f = `wings/${k}.png`; await put(f, await png(cv)); frag.wings[k] = f; }
  for (const [k, e] of R.faces) if (!m.faces?.[k]) { const f = `faces/${k}.bin`; await put(f, await gzip(e.buf)); frag.faces[k] = { file: f, family: e.family }; }
  await put(`fragments/world-${Date.now()}-${Math.floor(Math.random() * 1e6)}.json`, JSON.stringify(frag));
  return { tiles: Object.keys(frag.tiles).length, wings: Object.keys(frag.wings).length, faces: Object.keys(frag.faces).length, maps: Object.keys(frag.maps).length,
           town: Object.values(frag.buildings).reduce((n, e) => n + Object.keys(e.groups).length, 0), used: frag.used.length };
}

// (the early part runs as this module is imported -- not in the generator, which makes the cache afresh, nor in a worker)
EARLY = HERE && typeof document !== "undefined" && !/pregen\.html$/.test(HERE.pathname) ? loadEarly() : Promise.resolve(null);
await EARLY;
