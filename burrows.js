// BURROWS (2026-11-08): the dens of the animals that dig -- a badger's sett, a fox's earth, a wolf's or a hyena's den,
// a bear's den in a hillside, a porcupine's, a pangolin's, a skunk's, a rat's run, a puffin's burrow on the cliff top, a
// wolf spider's shaft -- each a HOLE IN THE GROUND that a tunnel goes down from, with the earth dug out of it heaped in
// front, where the world's animals of that kind live; the animal now and then goes home, stands at the mouth, and goes in.
//
// THE HOLE IS A REAL ONE. The ground is not depressed or painted dark: it is CUT -- the terrain's own pixels inside the
// mouth's oval are discarded (grass.js PITS, the same groundHole the cellars and the pyramid's passage use: the ground's
// material, the grass mask and the water all ask it), and under it lies the tunnel: a tube of earth going down into the
// hill at the burrow's `dip`, levelling off and turning, ending in a rounded chamber. The tube is the cylinder the oval is
// the cut of: its lines run along the tunnel's axis from the cut's edge, so the hole's rim IS the tube's top, and the
// tube's walls fall away under the cut edge exactly -- there is no collar to meet the terrain and no seam to hide.
//   What makes it watertight is that the rim follows the DRAWN ground, not groundH: the terrain's tiles stray up to
// `tol` (15 cm) from the height function between their vertices, so the rim and the earth round it are laid on the
// triangles the terrain is actually drawn with (terrainSampler: read from its meshes once they have arrived), a couple of
// centimetres under them. Round the rim a FLANGE of earth runs out under the ground: wherever the cut and the tube's top
// disagree by a hair, and wherever a low glance passes under the cut's far edge, what is seen is earth, never the sky.
// The tunnel's walls darken with the distance in (vertex colour: the light does not go down a hole), so from the
// usual heights a mouth reads as a dark opening with a lit lip, and from close and above as a tunnel going down.
//
// THE SPOIL HEAP: the earth out of the tunnel, a low fan of bare soil before the mouth, highest a little way out, the
// beaten run to the hole worn into it as a trough -- a mound on the drawn ground, its edge just under it (no seam), one
// small mesh a burrow (the grass mask's occluder: nothing grows through it; snow lies on it).
//
// What a burrow is lives in its asset (assets/nature/burrows/*.json: radius, dip, length, the heap, how many mouths, and
// which species dig it -- `species`); where it goes and who lives there is the world's (index.html). Frame cost: one
// draw for every tunnel together, one a heap; the oval test in the ground's shader only inside the box round them all.
//
//   const S = terrainSampler(groundGroup, [{ x, z, r }])     // the drawn ground's height near those spots
//   const B = burrowMesh(spec, site, S.at, { seed })         // one burrow's tunnel, flange and heap -> geometry + pits
//   const den = makeDen(w, an, mouth, env)                    // a wanderer that goes home to it -> { step(t, dt) }
import * as THREE from "three";
import { rng } from "./flora.js";
const D_EXP = 3.2;   // the mouth's D: grass.js PITS.d (the same number: what is cut and what the tube's rim fits)

export const BURROW = {
  sink: .018,     // metres the rim lies under the drawn ground
  flange: .028,   // ...and the flange's outer edge
  earth: "#5e4630", spoil: "#7f6142", deep: "#120d09",   // (each asset may give its own)
  seg: 22,        // round a tube
};

// THE DRAWN GROUND'S HEIGHT: the terrain's triangles near the given spots, gathered once from its meshes (world
// coordinates, as terrain.js builds them; a tile's skirt -- its vertical curtain -- left out). -> { at(x, z), has(x, z) }
// at() falls back on `fallback` (groundH) outside every spot.
export function terrainSampler(ground, spots, fallback = () => 0) {
  const sets = spots.map(() => []);
  const meshes = [];
  ground?.traverse?.((o) => { if (o.isMesh && o.geometry?.attributes?.position) meshes.push(o); });
  for (const m of meshes) {
    const g = m.geometry, P = g.attributes.position.array, I = g.index ? g.index.array : null;
    if (!g.boundingSphere) g.computeBoundingSphere();
    const bs = g.boundingSphere;
    const near = spots.map((s, k) => Math.hypot(bs.center.x - s.x, bs.center.z - s.z) < bs.radius + s.r ? k : -1).filter((k) => k >= 0);
    if (!near.length) continue;
    const n = I ? I.length : P.length / 3;
    for (let t = 0; t < n; t += 3) {
      const a = (I ? I[t] : t) * 3, b = (I ? I[t + 1] : t + 1) * 3, c = (I ? I[t + 2] : t + 2) * 3;
      const ax = P[a], az = P[a + 2], bx = P[b], bz = P[b + 2], cx = P[c], cz = P[c + 2];
      const area = (bx - ax) * (cz - az) - (cx - ax) * (bz - az);
      if (Math.abs(area) < 1e-6) continue;   // (a skirt: no extent on the plan)
      const x0 = Math.min(ax, bx, cx), x1 = Math.max(ax, bx, cx), z0 = Math.min(az, bz, cz), z1 = Math.max(az, bz, cz);
      for (const k of near) {
        const s = spots[k];
        if (x1 < s.x - s.r || x0 > s.x + s.r || z1 < s.z - s.r || z0 > s.z + s.r) continue;
        sets[k].push(ax, P[a + 1], az, bx, P[b + 1], bz, cx, P[c + 1], cz);
      }
    }
  }
  const tri = (L, x, z) => {
    for (let i = 0; i < L.length; i += 9) {
      const ax = L[i], ay = L[i + 1], az = L[i + 2], bx = L[i + 3], by = L[i + 4], bz = L[i + 5], cx = L[i + 6], cy = L[i + 7], cz = L[i + 8];
      const d = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz);
      const u = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / d, v = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / d, w = 1 - u - v;
      if (u >= -1e-5 && v >= -1e-5 && w >= -1e-5) return u * ay + v * by + w * cy;
    }
    return null;
  };
  const has = (x, z) => spots.some((s, k) => sets[k].length && Math.abs(x - s.x) <= s.r && Math.abs(z - s.z) <= s.r);
  return {
    has,
    tris: sets.reduce((n, L) => n + L.length / 9, 0),
    at(x, z) {
      for (let k = 0; k < spots.length; k++) {
        const s = spots[k];
        if (Math.abs(x - s.x) > s.r || Math.abs(z - s.z) > s.r) continue;
        const y = tri(sets[k], x, z);
        if (y !== null) return y;
      }
      return fallback(x, z);
    },
  };
}

const hex = (h) => new THREE.Color(h);
const smooth = (u) => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
const hash2 = (i, j) => { const h = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return h - Math.floor(h); };
const vnoise = (x, z) => {   // smooth value noise, 0..1
  const i = Math.floor(x), j = Math.floor(z), fx = x - i, fz = z - j, sx = fx * fx * (3 - 2 * fx), sz = fz * fz * (3 - 2 * fz);
  const a = hash2(i, j), b = hash2(i + 1, j), c = hash2(i, j + 1), d = hash2(i + 1, j + 1);
  return a + (b - a) * sx + (c - a) * sz + (a - b - c + d) * sx * sz;
};

// ONE BURROW: `spec` its asset (r, dip, len, bend, turn, chamber, heap...), `site` { x, z, yaw (into the hill: the tunnel
// runs along (cos yaw, sin yaw) on the plan), mouths: [{ x, z, yaw }] (a sett's several; else the site's one) },
// `hAt(x, z)` the DRAWN ground's height. -> { tunnel: {P, C, I}, heap: {P, C, I}, pits: [...], mouths: [{ ...floor(s) }],
//   top(x, z): the heap's top where it is higher than the ground (for an animal walking over it), else null }
export function burrowMesh(spec, site, hAt, { seed = 1 } = {}) {
  const r0 = spec.r ?? .15, R = rng(seed * 131 + 7);
  const earth = hex(spec.earth ?? BURROW.earth), spoil = hex(spec.spoil ?? BURROW.spoil), deep = hex(spec.deep ?? BURROW.deep);
  const earthLit = earth.clone().lerp(spoil, .65);   // (the walls by the lip, in the light)
  const T = { P: [], C: [], I: [] }, H = { P: [], C: [], I: [] }, pits = [], mouths = [], heaps = [];
  const c = new THREE.Color();
  const put = (G, x, y, z, col) => { G.P.push(x, y, z); G.C.push(col.r, col.g, col.b); return G.P.length / 3 - 1; };
  const quadGrid = (G, base, cols, rows, wrap) => {   // rows x cols vertices from `base`, row-major; wrap: the columns close round
    for (let j = 0; j < rows - 1; j++) for (let k = 0; k < (wrap ? cols : cols - 1); k++) {
      const k1 = (k + 1) % cols, a = base + j * cols + k, b = base + j * cols + k1, d = base + (j + 1) * cols + k, e = base + (j + 1) * cols + k1;
      G.I.push(a, d, b, b, d, e);
    }
  };
  for (const m of site.mouths ?? [{ x: site.x, z: site.z, yaw: site.yaw }]) {
    const r = r0 * (m.scale ?? 1), NS = 2 * Math.max(7, Math.round((spec.seg ?? BURROW.seg) * Math.min(1.4, Math.max(.8, r / .15)) / 2));
    const dx = Math.cos(m.yaw), dz = Math.sin(m.yaw);
    // the ground's own slope along the tunnel at the mouth (+ rising into the hill)
    const beta = Math.atan2(hAt(m.x + dx * .5, m.z + dz * .5) - hAt(m.x - dx * .5, m.z - dz * .5), 1);
    // its dip: never so shallow to the ground that the cut runs out into a long slot (at least 18 deg between them)
    const al = Math.max((spec.dip ?? 30) * Math.PI / 180, .32 - beta);
    const ca = Math.cos(al), sa = Math.sin(al);
    const ax = [dx * ca, -sa, dz * ca], U = [dx * sa, ca, dz * sa], W = [-dz, 0, dx];
    const y0 = hAt(m.x, m.z);
    // the tube's cross-section: round, the floor a little flatter (dug and trodden), a few lumps along the wall
    const ph = R() * 6.28;
    const off = (k) => {
      const f = k / NS * Math.PI * 2, cu = Math.cos(f), su = Math.sin(f), lump = 1 + .06 * Math.sin(3 * f + ph) + .04 * Math.sin(5 * f + ph * 2);
      const u = r * lump * (cu < 0 ? -Math.min(-cu, .62) : cu), w = r * lump * su;   // (a D: an arched roof, a flat trodden floor)
      return [U[0] * u + W[0] * w, U[1] * u + W[1] * w, U[2] * u + W[2] * w];
    };
    const Q = Array.from({ length: NS }, (_, k) => { const o = off(k); return [m.x + o[0], y0 + o[1], m.z + o[2]]; });
    // where each of the tube's lines comes up through the drawn ground (a hair under it): bisection along the line
    const reach = 3 * r / Math.sin(Math.max(.25, al + beta)) + .6;
    const s0 = Q.map((q) => {
      const f = (s) => q[1] + ax[1] * s - (hAt(q[0] + ax[0] * s, q[2] + ax[2] * s) - BURROW.sink);
      let lo = -reach, hi = reach;
      if (f(lo) < 0) return lo; if (f(hi) > 0) return hi;
      for (let i = 0; i < 26; i++) { const mid = (lo + hi) / 2; if (f(mid) > 0) lo = mid; else hi = mid; }
      return (lo + hi) / 2;
    });
    const sMin = Math.min(...s0), sMax = Math.max(...s0);
    // THE AXIS: straight down at the dip for L1, then easing level and turning (bend, turn), then the chamber
    const L1 = sMax + Math.max(r * 1.5, (spec.len ?? 1.2) * .5), L2 = Math.max(r * 2, (spec.len ?? 1.2) * .7);
    const turn = (spec.turn ?? 40) * Math.PI / 180 * (R() < .5 ? -1 : 1), dipEnd = (spec.level ?? 6) * Math.PI / 180;
    const chamberR = r * (spec.chamber ?? 1.7), CL = chamberR * 2.2;
    const step = Math.max(.03, r * .45);
    const sig = [];
    for (let s = sMin; s < L1; s += step) sig.push(s);
    sig.push(L1);
    // the frames along it: position, dir, up, side -- straight to L1, then integrated
    const frames = [];
    const sideOf = (dir) => { const l = Math.hypot(dir[2], dir[0]) || 1; return [-dir[2] / l, 0, dir[0] / l]; };
    const upOf = (dir, side) => [side[1] * dir[2] - side[2] * dir[1], side[2] * dir[0] - side[0] * dir[2], side[0] * dir[1] - side[1] * dir[0]];
    for (const s of sig) frames.push({ s, p: [m.x + ax[0] * s, y0 + ax[1] * s, m.z + ax[2] * s], dir: ax, rad: 1 });
    {
      let p = frames[frames.length - 1].p.slice(), yaw = m.yaw, dip = al;
      const n2 = Math.ceil(L2 / step), nC = Math.max(4, Math.ceil(CL / step));
      for (let i = 1; i <= n2 + nC; i++) {
        const u = Math.min(1, i / n2), ds = i <= n2 ? L2 / n2 : CL / nC;
        dip = al + (dipEnd - al) * smooth(u); yaw = m.yaw + turn * smooth(u);
        const dir = [Math.cos(yaw) * Math.cos(dip), -Math.sin(dip), Math.sin(yaw) * Math.cos(dip)];
        p = [p[0] + dir[0] * ds, p[1] + dir[1] * ds, p[2] + dir[2] * ds];
        // the chamber: the tube swelling to chamberR over its first third, then closing in a round end
        let rad = 1;
        if (i > n2) { const v = (i - n2) / nC; rad = v < .35 ? 1 + (chamberR / r - 1) * smooth(v / .35) : (chamberR / r) * Math.sqrt(Math.max(0, 1 - ((v - .35) / .65) ** 2)); }
        frames.push({ s: frames[frames.length - 1].s + ds, p, dir, rad: Math.max(rad, .001) });
      }
    }
    // THE TUBE: ring j, column k -- on the straight stretch the line from Q_k (clamped at its cut), beyond in its frame
    const base = T.P.length / 3;
    const lightAt = (k, s) => {   // how much light reaches this far in, this side (the floor catches more than the roof)
      const d = Math.max(0, s - s0[k]), f = k / NS * Math.PI * 2;
      return Math.exp(-d / (r * 1.3 + .03)) * (.8 - .2 * Math.cos(f));   // (the walls by the lip lit earth, going dark a couple of tunnel-widths in)
    };
    for (const F of frames) {
      const straight = F.s <= L1 + 1e-6;
      const side = sideOf(F.dir), up = upOf(F.dir, side);
      for (let k = 0; k < NS; k++) {
        let x, y, z;
        if (straight) { const s = Math.max(F.s, s0[k]); x = Q[k][0] + ax[0] * s; y = Q[k][1] + ax[1] * s; z = Q[k][2] + ax[2] * s; }
        else {
          const f = k / NS * Math.PI * 2, cu = Math.cos(f), su = Math.sin(f), lump = 1 + .06 * Math.sin(3 * f + ph) + .04 * Math.sin(5 * f + ph * 2) + .05 * Math.sin(F.s * 9 + f * 2);
          const u = r * F.rad * lump * (cu < 0 ? -Math.min(-cu, .62) : cu), w = r * F.rad * lump * su;
          x = F.p[0] + up[0] * u + side[0] * w; y = F.p[1] + up[1] * u + side[1] * w; z = F.p[2] + up[2] * u + side[2] * w;
        }
        c.copy(deep).lerp(earthLit, Math.min(1, lightAt(k, F.s)));
        put(T, x, y, z, c);
      }
    }
    quadGrid(T, base, NS, frames.length, true);
    { const e = put(T, ...frames[frames.length - 1].p, deep), last = base + (frames.length - 1) * NS; for (let k = 0; k < NS; k++) T.I.push(last + k, e, last + (k + 1) % NS); }
    // THE FLANGE: from the rim out under the ground, two rings (the earth seen past the cut's edge)
    const rim = s0.map((s, k) => [Q[k][0] + ax[0] * s, Q[k][1] + ax[1] * s, Q[k][2] + ax[2] * s]);
    const fb = T.P.length / 3, FL = .1 + r * 1.2;
    const lip = new THREE.Color().copy(earth).multiplyScalar(.82);
    for (const [ring, out, sink] of [[0, 0, BURROW.sink], [1, FL * .35, (BURROW.sink + BURROW.flange) / 2], [2, FL, BURROW.flange]]) {
      for (let k = 0; k < NS; k++) {
        const [px, , pz] = rim[k], ox = px - m.x, oz = pz - m.z, l = Math.hypot(ox, oz) || 1, x = px + ox / l * out, z = pz + oz / l * out;
        put(T, x, ring ? hAt(x, z) - sink : rim[k][1], z, lip);
      }
    }
    quadGrid(T, fb, NS, 3, true);
    // THE CUT: the oval the ground is discarded inside -- the rim's own extent along and across (the nearer side of each,
    // so the cut stays inside the tube's top; the flange shows wherever they part by a hair)
    {
      const uv = rim.map(([px, , pz]) => [(px - m.x) * dx + (pz - m.z) * dz, (pz - m.z) * dx - (px - m.x) * dz]);
      const u0 = Math.min(...uv.map((q) => q[0])), u1 = Math.max(...uv.map((q) => q[0])), v0 = Math.min(...uv.map((q) => q[1])), v1 = Math.max(...uv.map((q) => q[1]));
      const cu = (u0 + u1) / 2, cv = (v0 + v1) / 2, a0 = (u1 - u0) / 2, b0 = (v1 - v0) / 2;
      // (shrunk till every rim point lies on or outside it: the oval inside the tube's top)
      // (a D, as grass.js tests it: its near half squarer, |u|^PITS.d -- each rim point's scale found by halving)
      const dIn = (u, v) => (u < 0 ? Math.abs(u) ** D_EXP : u * u) + v * v;
      const k = Math.min(1, ...uv.map(([u, v]) => {
        const un = (u - cu) / a0, vn = (v - cv) / b0;
        let lo = .01, hi = 3;
        for (let i = 0; i < 30; i++) { const mid = (lo + hi) / 2; if (dIn(un / mid, vn / mid) > 1) lo = mid; else hi = mid; }
        return lo;
      }));
      if (a0 > 1e-3 && b0 > 1e-3) pits.push({ x: m.x + dx * cu - dz * cv, z: m.z + dz * cu + dx * cv, ca: dx, sa: dz, a: a0 * k * .985, b: b0 * k * .985 });
    }
    // the floor line, for an animal going in: s from the front of the cut (its rim's lowest line) down the tunnel
    const kF = Math.round(NS / 2), front = s0[kF], q = Q[kF];
    mouths.push({ x: m.x, z: m.z, yaw: m.yaw, dx, dz, dip: al, r, sFront: front, sIn: Math.min(L1, front + r * 4 + .25),
                  floor: (s) => [q[0] + ax[0] * s, q[1] + ax[1] * s, q[2] + ax[2] * s],
                  apron: [rim[kF][0] - dx * (r * 1.2 + .15), rim[kF][2] - dz * (r * 1.2 + .15)] });
    // THE SPOIL HEAP before it (`heap`: { len, wide, h } metres, x the burrow's radius when under 1): a fan of bare earth
    const hp = spec.heap ?? {};
    const HL = (hp.len ?? 6) * r, HW = (hp.wide ?? 5) * r, HH = (hp.h ?? 1.3) * r * (.8 + .4 * R());
    if (HH > .005) {
      // (its back edge at the cut's front lip: the oval's own, which can sit inside the tube's rim -- from the rim the
      //  heap stood off the hole with a strip of grass between)
      const P = pits[pits.length - 1], lipU = P ? (P.x - m.x) * dx + (P.z - m.z) * dz - P.a : (rim[kF][0] - m.x) * dx + (rim[kF][2] - m.z) * dz;
      const fx = m.x + dx * (lipU + .025), fz = m.z + dz * (lipU + .025);   // (its sunk edge a little inside: it comes out of the ground AT the lip)
      const cx = fx - dx * HL / 2, cz = fz - dz * HL / 2, NR = 16, NA = 48, hb = H.P.length / 3, seedN = R() * 1000;
      const groove = r * 1.1, Pq = pits[pits.length - 1];
      if (Pq) Pq.hl = HL;   // (the bare earth under it: grass.js groundEarth)
      // a FAN: narrow at the mouth, spreading out down the slope (v's half-width grows along u)
      const fan = (u) => .62 + .38 * smooth((u + 1) / 2);
      const lumpAt = (x, z) => (vnoise(x / (r * 1.3) + seedN, z / (r * 1.3)) - .5) * .5 + (vnoise(x / (r * .45) - seedN, z / (r * .45)) - .5) * .22;
      const edge = (u, v) => { const f = Math.atan2(v, u); return 1 + .07 * Math.sin(3 * f + seedN) + .05 * Math.sin(7 * f + seedN * 1.7) + .03 * Math.sin(13 * f - seedN); };
      // (blunt at the mouth's end, a D, not tapering to a point at the hole: that end |u|^3)
      const dHeap = (u, v) => u < 0 ? Math.sqrt((-u) ** 3 + v * v) : Math.hypot(u, v);
      const reach = (cf, sf) => { let lo = .5, hi = 2; for (let it = 0; it < 24; it++) { const t = (lo + hi) / 2; if (dHeap(t * cf, t * sf) < 1) lo = t; else hi = t; } return lo; };
      const apron = new THREE.Color(.27, .17, .085);   // (grass.js earthOver's bare earth: the heap's toe goes into it)
      const height = (u, v, x = null, z = null) => {   // u along (-1 at the mouth's lip .. 1 out), v across (-1..1) -> metres over the ground
        const rho = dHeap(u, v) / edge(u, v);   // (its outline ragged, not an ellipse)
        if (rho >= 1) return 0;
        const peak = Math.exp(-((u + .45) ** 2) * 1.8);   // (highest near the hole: the earth thrown out of it lands there)
        let h = HH * (1 - rho * rho) ** 1.05 * (.5 + .6 * peak) * (.3 + .7 * smooth((u + 1) / .45));   // (its toe running out low into the ground, not a cliff; ramping up from the lip)
        h *= 1 - (.5 + .25 * smooth((-.2 - u) / .6)) * Math.exp(-(((v * HW / 2 * fan(u)) / groove) ** 2)) * smooth((.85 - u) / .6);   // the run down its middle, worn in by the comings and goings
        h += HH * .32 * Math.exp(-(((u + 1) / .16) ** 2)) * Math.sqrt(Math.max(0, 1 - v * v * 1.6)) * (1 - Math.exp(-((v / .35) ** 2)));   // (broken in the middle where the run goes in)   // (a lip of thrown earth at the hole's edge: no strip of grass between)
        if (x !== null) h *= 1 + lumpAt(x, z) * (.4 + .6 * smooth(h / (HH * .3 + 1e-6)));   // lumps and clods in its surface
        return Math.max(0, h);
      };
      const at = (u, v) => [cx - dx * u * HL / 2 - dz * v * HW / 2 * fan(u), cz - dz * u * HL / 2 + dx * v * HW / 2 * fan(u)];
      for (let i = 0; i <= NR; i++) for (let k = 0; k < NA; k++) {
        const f = k / NA * Math.PI * 2, rho = (i / NR) ** .8 * edge(Math.cos(f), Math.sin(f)) * reach(Math.cos(f), Math.sin(f)), u = rho * Math.cos(f), v = rho * Math.sin(f);
        const [x, z] = at(u, v);
        const h = height(u, v, x, z), y = hAt(x, z) + h - (i === NR ? .03 : .012 * (1 - smooth(h / .02)));
        // its colour: fresh and darker by the mouth, drying paler on the crown, trodden darker down the run
        const run = Math.exp(-(((v * HW / 2 * fan(u)) / groove) ** 2)) * smooth((.85 - u) / .6);
        c.copy(spoil).multiplyScalar((.8 + .32 * vnoise(x * 9 + seedN, z * 9) + .12 * Math.min(1, h / (HH + 1e-6))) * (1 - .22 * run) * (1 - .12 * Math.exp(-(((u + 1) / .3) ** 2))));
        c.lerp(apron, .6 * (1 - smooth(h / (HH * .25 + 1e-6))));   // (its thin toe the same earth as the ground round it)
        put(H, x, y, z, c);
      }
      for (let i = 0; i < NR; i++) for (let k = 0; k < NA; k++) {
        const k1 = (k + 1) % NA, a = hb + i * NA + k, b = hb + i * NA + k1, d = hb + (i + 1) * NA + k, e = hb + (i + 1) * NA + k1;
        H.I.push(a, d, b, b, d, e);   // (facing up)
      }
      // (ring 0 is the centre point itself, repeated: its quads are the centre's fan)
      // CLODS of earth and a few STONES out of the digging lying on it, (a sett's) BEDDING -- old dry grass dragged out
      const area = HL * HW / (r * r * 27);
      const lump = (u, v, size, flat, col, len = 1, yaw = R() * 6.28) => {
        const [x, z] = at(u, v), y = hAt(x, z) + height(u, v, x, z), b0 = H.P.length / 3, cy = Math.cos(yaw), sy = Math.sin(yaw);
        const O = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
        for (const [ox, oy, oz] of O) {
          const j = .75 + .5 * R(), lx = ox * size * len * j, lz = oz * size * j, ly = oy * size * flat * j;
          put(H, x + lx * cy - lz * sy, y + ly + size * flat * .35, z + lx * sy + lz * cy, c.copy(col).multiplyScalar(.85 + .3 * R()));
        }
        for (const [a, b, d] of [[0, 2, 4], [4, 2, 1], [1, 2, 5], [5, 2, 0], [4, 3, 0], [1, 3, 4], [5, 3, 1], [0, 3, 5]]) H.I.push(b0 + a, b0 + d, b0 + b);
      };
      const clodC = new THREE.Color().copy(spoil).multiplyScalar(.82), stoneC = hex(spec.stone ?? "#8d877b"), strawC = hex("#b49a5c");
      const nCl = Math.round((spec.clods ?? 36) * Math.min(3, area)), nSt = Math.round((spec.stones ?? 5) * Math.min(3, area));
      for (let i = 0; i < nCl; i++) { const a = R() * 6.28, q = Math.sqrt(R()) * .92; lump(q * Math.cos(a), q * Math.sin(a), r * (.07 + .16 * R() ** 2), .7, clodC); }
      for (let i = 0; i < nSt; i++) { const a = R() * 6.28, q = Math.sqrt(R()) * .9; lump(q * Math.cos(a), q * Math.sin(a), r * (.1 + .17 * R()), .45, stoneC); }
      for (let i = 0; i < (spec.bedding ?? 0); i++) { const u = -1 + R() * 1.1, v = (R() - .5) * 1.2; lump(u, v, .007, .5, strawC, 9 + 8 * R()); }
      // ROOTS over the mouth (a fox's earth under a hedge's or a tree's roots): arcs across its back, ends in the ground
      for (let i = 0; i < (spec.roots ?? 0); i++) {
        const P0 = pits[pits.length - 1], a0 = P0 ? P0.a : r, b0 = P0 ? P0.b : r, pu = P0 ? (P0.x - m.x) * dx + (P0.z - m.z) * dz : 0;
        const uc = pu + a0 * (.15 + .7 * R()), w = b0 * 1.3 + .1 + R() * .15, lift = r * (.08 + .18 * R()), rr = .012 + .018 * R(), tw = (R() - .5) * .5;
        const NSG = 10, NSD = 6, rb = H.P.length / 3, bark = hex("#55463a");
        for (let j = 0; j <= NSG; j++) {
          const t = j / NSG, vv = (t * 2 - 1) * w, uu = uc + tw * (t - .5) * w, px = m.x + dx * uu - dz * vv, pz = m.z + dz * uu + dx * vv;
          const py = hAt(px, pz) + lift * Math.sin(Math.PI * t) ** .8 - .09 * (1 - Math.sin(Math.PI * t)) + rr * .3;
          for (let k = 0; k < NSD; k++) {
            const f = k / NSD * Math.PI * 2, rad = rr * (1.15 - .3 * Math.abs(t - .5));
            put(H, px + dx * Math.cos(f) * rad, py + Math.sin(f) * rad, pz + dz * Math.cos(f) * rad, c.copy(bark).multiplyScalar(.8 + .35 * R()));
          }
        }
        quadGrid(H, rb, NSD, NSG + 1, true);
      }
      heaps.push({ cx, cz, dx, dz, HL, HW, height, fan });
    }
  }
  const top = (x, z) => {
    let best = 0;
    for (const h of heaps) {
      const ox = x - h.cx, oz = z - h.cz, u = -(ox * h.dx + oz * h.dz) / (h.HL / 2), v = (oz * h.dx - ox * h.dz) / (h.HW / 2 * h.fan(u));
      if (Math.abs(u) < 1.2 && Math.abs(v) < 1.2) best = Math.max(best, h.height(u, v));
    }
    return best;
  };
  return { tunnel: T, heap: H, pits, mouths, top };
}

// geometry arrays -> a mesh (normals made here; lit materials want them)
export function burrowGeometry(G) {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(G.P, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(G.C, 3));
  g.setIndex(G.I);
  g.computeVertexNormals();
  return g;
}

// WHERE A BURROW GOES: in its animals' range, on the ground that suits it -- a bank or a slope (`slope`: [least, most],
// rise over run) facing out of the hill, dry, clear of the sites, the roads, the trees, the water (ok(x, z, m) says so,
// m the clearance) -- the tunnel running INTO the hill (uphill), a flat spot any way round. `spawn()` draws a point in
// the range; `near` [x, z] (its animals' middle) is preferred. -> { x, z, yaw, mouths: [...] } or null
export function findBurrowSite(spec, { spawn, near, groundH, ok, r: rand, avoid = [] }) {
  const sl = spec.slope ?? [.05, .6], clear = (spec.r ?? .15) * (spec.heap?.len ?? 6) * .6 + 1;
  const grad = (x, z) => [(groundH(x + .7, z) - groundH(x - .7, z)) / 1.4, (groundH(x, z + .7) - groundH(x, z - .7)) / 1.4];
  let best = null, bs = -1e9;
  for (let i = 0; i < 90; i++) {
    const [x, z] = spawn();
    if (!ok(x, z, clear) || avoid.some((a) => Math.hypot(a.x - x, a.z - z) < a.r + clear + 2)) continue;
    const [gx, gz] = grad(x, z), s = Math.hypot(gx, gz);
    let score = -Math.max(0, sl[0] - s) * 8 - Math.max(0, s - sl[1]) * 8 + Math.min(s, sl[1]) * (spec.bank ? 3 : 1);
    if (near) score -= Math.hypot(near[0] - x, near[1] - z) * .02;
    score += rand() * .05;
    if (score > bs) { bs = score; best = { x, z, yaw: s > .03 ? Math.atan2(gz, gx) : rand() * Math.PI * 2 }; }
  }
  if (!best) return null;
  // a sett's other mouths: round the first, within `spread` m, each into its own bit of the hill
  const mouths = [{ x: best.x, z: best.z, yaw: best.yaw, scale: 1 }];
  for (let i = 1, tries = 0; i < (spec.mouths ?? 1) && tries < 40; tries++) {
    const a = rand() * Math.PI * 2, d = (spec.spread ?? 3) * (.5 + .5 * rand()), x = best.x + Math.cos(a) * d, z = best.z + Math.sin(a) * d;
    if (!ok(x, z, clear * .7) || mouths.some((q) => Math.hypot(q.x - x, q.z - z) < (spec.r ?? .15) * 12)) continue;
    const [gx, gz] = grad(x, z), s = Math.hypot(gx, gz);
    mouths.push({ x, z, yaw: s > .03 ? Math.atan2(gz, gx) : best.yaw + (rand() - .5) * 1.4, scale: .8 + .3 * rand() });
    i++;
  }
  return { ...best, mouths };
}

// GOING HOME: a wanderer with a den (`w` its wanderer, `an` its figure, `m` a mouth of burrowMesh's). Now and then
// (every `visit` seconds or so) it walks to the mouth, stands there looking about, and half the time goes in -- down the
// tunnel's floor, nose down, out of sight -- and comes out again a while later, nose up, to stand at the mouth before
// it wanders off. One out of its hours (`active`: a badger by day) goes home and stays in till its time comes round;
// a shy one that you come near while it is by its mouth bolts in. Its stream of randoms is its own (w.rng): what it does
// is a function of the clock, as the rest of the wanderers'.
//   env: { groundH, top(x, z) (the heap's), out() (is it its time to be about), near() (metres to you), shy, visit: [a, b] }
//   -> { step(t, dt) }: true while it has the tick (on its way home, at the mouth, in, coming out)
export function makeDen(w, an, m, env) {
  const D = { st: "start", next: 0, till: 0, s: 0, go: false, hurry: false };
  const visit = env.visit ?? [70, 260];
  const into = Math.atan2(-m.dz, m.dx), outOf = into + Math.PI;   // (a heading: forward (cos h, -sin h) on the plan)
  const wrap = (v) => ((v + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
  const standY = (x, z) => env.groundH(x, z) + (env.top?.(x, z) ?? 0);
  const settle = (dt) => { w.animT += (Math.round(w.animT * 2 * w.hz) / (2 * w.hz) - w.animT) * Math.min(1, dt * 10); w.setT(w.animT, undefined, undefined, false, false); };
  const walk = (dt, v) => { w.animT += dt * v / w.base; w.setT(w.animT, undefined, undefined, true, v > w.speed * 1.8); };
  const turnTo = (h, dt, k = 4) => { w.heading += Math.max(-k * dt, Math.min(k * dt, wrap(h - w.heading))); w.apply(w.heading); };
  const pitchTo = (p, dt) => { an.pitch = (an.pitch ?? 0) + (p - (an.pitch ?? 0)) * Math.min(1, dt * 5); };
  D.step = (t, dt) => {
    const out = env.out ? env.out() : true;
    if (D.st === "start") {   // (the world's first tick: one out of its hours begins in its den)
      if (!out) { D.st = "inside"; an.hidden = true; D.till = Infinity; return true; }
      D.st = "out"; D.next = t + visit[0] * .3 + w.rng() * visit[1] * .6;
    }
    if (D.st === "out") {
      const scared = env.shy && env.near && env.near() < env.shy && Math.hypot(w.p.x - m.x, w.p.z - m.z) < 25;
      if (out && t < D.next && !scared) return false;
      D.st = "home"; D.go = !out || scared || w.rng() < .55; D.hurry = !!scared;
    }
    if (D.st === "home") {
      const [tx, tz] = m.apron, ddx = tx - w.p.x, ddz = tz - w.p.z, d = Math.hypot(ddx, ddz);
      const v = w.speed * (D.hurry ? 3 : 1.15);
      if (d < Math.max(.12, v * dt)) {
        w.p.set(tx, standY(tx, tz), tz); D.st = "mouth"; D.till = t + (D.hurry ? .2 : 3 + w.rng() * 8); return true;
      }
      turnTo(Math.atan2(-ddz, ddx), dt, D.hurry ? 8 : 3);
      const k = Math.min(1, v * dt / d);
      w.p.x += ddx * k; w.p.z += ddz * k; w.p.y = standY(w.p.x, w.p.z);
      walk(dt, v); pitchTo(0, dt);
      return true;
    }
    if (D.st === "mouth") {   // stood before it, looking about, then in (or off again)
      turnTo(into + (t < D.till - 1.5 ? .5 * Math.sin(t * .9 + w.speed * 7) : 0), dt, 2.5);
      settle(dt); pitchTo(0, dt);
      const scared = env.shy && env.near && env.near() < env.shy;
      if (scared) { D.go = true; D.hurry = true; D.till = Math.min(D.till, t); }
      if (t < D.till) return true;
      if (D.go || !out) { D.st = "in"; D.s = m.sFront - .2; return true; }
      D.st = "out"; D.next = t + visit[0] + w.rng() * (visit[1] - visit[0]); return false;
    }
    if (D.st === "in") {   // down the floor, nose down
      const v = w.speed * (D.hurry ? 2.2 : .7);
      D.s += v * dt; turnTo(into, dt, 6);
      const [fx, fy, fz] = m.floor(Math.max(D.s, m.sFront)), [ax, az] = m.apron, u = smooth((D.s - (m.sFront - .2)) / .2);
      w.p.set(ax + (fx - ax) * u, standY(ax, az) + (fy - standY(ax, az)) * u, az + (fz - az) * u);
      pitchTo(-m.dip * .8 * u, dt); walk(dt, v);
      if (D.s > m.sIn) { D.st = "inside"; an.hidden = true; an.pitch = 0; D.till = out ? t + 15 + w.rng() * 50 : Infinity; }
      return true;
    }
    if (D.st === "inside") {
      if (D.till === Infinity && out) D.till = t + 2 + w.rng() * 30;   // (its time come round: out in a little while)
      if (t < D.till) return true;
      D.st = "up"; D.s = m.sIn; an.hidden = false; w.heading = outOf; w.apply(w.heading); an.pitch = m.dip * .8;
      return true;
    }
    if (D.st === "up") {   // up the floor, nose up, onto the apron
      const v = w.speed * .6;
      D.s -= v * dt;
      if (D.s <= m.sFront - .2) { const [ax, az] = m.apron; w.p.set(ax, standY(ax, az), az); D.st = "look"; D.till = t + 3 + w.rng() * 7; return true; }
      const [fx, fy, fz] = m.floor(Math.max(D.s, m.sFront)), [ax, az] = m.apron, u = smooth((D.s - (m.sFront - .2)) / .2);
      w.p.set(ax + (fx - ax) * u, standY(ax, az) + (fy - standY(ax, az)) * u, az + (fz - az) * u);
      pitchTo(m.dip * .8 * u, dt); walk(dt, v);
      return true;
    }
    if (D.st === "look") {   // just out: a look round before it goes about its business
      turnTo(outOf + .6 * Math.sin(t * .7 + w.speed * 5), dt, 2); settle(dt); pitchTo(0, dt);
      if (!out) { D.st = "in"; D.s = m.sFront - .2; D.go = true; return true; }
      if (t < D.till) return true;
      an.pitch = 0; D.st = "out"; D.next = t + visit[0] + w.rng() * (visit[1] - visit[0]);
      return false;
    }
    return false;
  };
  return D;
}
