// MANES OF THORNS (2026-10-03): a lion's mane as spikes -- the lattice of hair's thorns (thorns.js) as a sleeve round
// the creature's NECK and the back of its head, where its definition has a mane (an `extras` ellipsoid with `thorns`:
// mammals.js reports it as def.mane -- the neck and the head it hugs -- and draws the soft ball no more; composite.js
// keeps it on the animal). Like the mesh heads (heads.js): built once per kind of mane, drawn as one InstancedMesh each,
// every copy placed each frame on the posed neck -- from its chest end along it toward the head, sized by how long it is
// now -- and shaded as hair is (heads.js faceMaterial: half-Lambert with the Kajiya-Kay sheen and the fibres, softer).
//   thorns: { rows, cols, every, arc ([from, to] radians round from straight up: a crest; none: a ring), along ([from, to] in neck lengths from its chest end: into the shoulders .. round the
//             back of the head), length (x the mane's radius), comb ([x, y, z] in the neck's frame: back and down), blend,
//             vary, inset (x the creature's radius there: the sleeve a little over the fur, never under it) }
import * as THREE from "three";
import { setCount } from "./bounds.js";   // (an empty pool not drawn)
import { thornLattice } from "./thorns.js";
import { faceMaterial, SHADE } from "./heads.js";

function rng(seed) {
  let a = (seed >>> 0) || 1;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const DEG = Math.PI / 180;

// the mane's geometry in the NECK's frame: x along the neck from its chest end (0) to its head end (neckLen), y up, z to
// the side. A SLEEVE round it: rows from `along[0]` neck lengths into the shoulders to `along[1]` (past the head's
// joint, round the back of the head), each at the radius the creature has there -- the chest's a little more than the
// neck's, the neck's own tapering, then the head's -- `inset` times it: a little OVER the fur (its blended surface stands
// out past the parts' own radii), so between the thorns there is mane, not the neck's skin; open at
// both ends (the face stands out of the front one)
export function maneGeometry(mane, seed = 7) {
  const T = { rows: 9, cols: 22, every: 3, along: [-0.45, 1.6], length: .7, comb: [-1, -.35, 0], blend: .45, vary: .4, inset: 1.15, ...(mane.thorns ?? {}) };
  const L = mane.neckLen, r = rng(seed), c = new THREE.Color(mane.color ?? "#8a5a1c");
  const cl = Math.hypot(...T.comb) || 1, comb = T.comb.map((v) => v / cl);
  const radiusAt = (x) => (x <= 0 ? mane.rA * 1.15 : x <= L ? mane.rA + (mane.rB - mane.rA) * x / L : Math.max(mane.rB, mane.headR * .92)) * T.inset;
  const pos = [], nor = [], col = [], uv = [], mask = [];
  // (`arc` [from, to]: radians round the neck from straight up, + toward its +z -- a CREST along the top of the neck, a
  //  horse's, not a ring round it; the lattice then open at its two edges)
  const arc = T.arc ?? null, fOf = (j) => (arc ? arc[0] + (arc[1] - arc[0]) * j / (T.cols - 1) : j / T.cols * 2 * Math.PI);
  thornLattice({ NR: T.rows, NC: T.cols, ring: !arc, every: T.every,
    at: (i, j) => { const x = L * (T.along[0] + (T.along[1] - T.along[0]) * i / T.rows), f = fOf(j), R = radiusAt(x);
                    const n = [0, Math.cos(f), Math.sin(f)];
                    return { q: [x, n[1] * R, n[2] * R], n, u: j * .37, v: i * .05 }; },
    spike: (i, j, n) => { const d = n.map((v, k) => v * (1 - T.blend) + comb[k] * T.blend), l = Math.hypot(...d);
                          return { d: d.map((v) => v / l), L: mane.r * T.length * (1 + (r() - .5) * T.vary) }; },
    inside: (m) => [m[0], 0, 0],   // (the neck's axis beside each face)
    tri: (A, B, C, n) => { for (const X of [A, B, C]) { pos.push(...X.q); nor.push(...n); col.push(c.r, c.g, c.b); uv.push(X.u, X.v); mask.push(1); } } });
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  geo.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  geo.setAttribute("hairMask", new THREE.Float32BufferAttribute(mask, 1));
  geo.setAttribute("wetMask", new THREE.Float32BufferAttribute(new Float32Array(mask.length), 1));   // (faceMaterial's wet shine: none on a mane)
  return geo;
}

export function createManes(scene, { cap = 32, shade = {} } = {}) {
  // (a mane's spikes are broad flat facets, not fine hair: a softer sheen than a head's, or they shine white)
  const mat = faceMaterial({ ...SHADE, ...shade, hair: { s1: .05, s2: .09, ...(shade.hair ?? {}) } });
  const kinds = new Map();   // the mane's numbers -> { mesh, n }
  const kindOf = (m) => {
    const key = `${m.r.toFixed(3)}|${m.neckLen.toFixed(3)}|${m.rA.toFixed(3)}|${m.headR.toFixed(3)}|${m.color}|${JSON.stringify(m.thorns)}`;
    if (!kinds.has(key)) {
      const mesh = new THREE.InstancedMesh(maneGeometry(m), mat, cap);
      setCount(mesh, 0); mesh.frustumCulled = false; scene.add(mesh);
      kinds.set(key, { mesh, n: 0 });
    }
    return kinds.get(key);
  };
  const M = new THREE.Matrix4(), X = new THREE.Vector3(), Y = new THREE.Vector3(), Z = new THREE.Vector3(), C = new THREE.Vector3(), H = new THREE.Vector3();
  return {
    place(herds) {
      for (const k of kinds.values()) k.n = 0;
      for (const herd of herds) for (const an of herd?.animals ?? []) {
        const m = an.mane;
        if (!m || an.hidden || an._off || an._out) continue;
        const k = kindOf(m);
        if (k.n >= cap) continue;
        // (the neck as it is posed now: its chest end the one further from the head, its axis toward the head, its length
        //  against its rest length for the size)
        const [n0, n1] = herd.ends(an, m.neck), [h0, h1] = herd.ends(an, m.head);
        H.set((h0[0] + h1[0]) / 2, (h0[1] + h1[1]) / 2, (h0[2] + h1[2]) / 2);
        const d0 = Math.hypot(n0[0] - H.x, n0[1] - H.y, n0[2] - H.z), d1 = Math.hypot(n1[0] - H.x, n1[1] - H.y, n1[2] - H.z);
        const [a, b] = d0 > d1 ? [n0, n1] : [n1, n0];
        C.set(a[0], a[1], a[2]);
        X.set(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
        const nl = X.length();
        X.normalize();
        Y.set(0, 1, 0).addScaledVector(X, -X.y).normalize();
        Z.crossVectors(X, Y);
        const s = m.neckLen && nl > 1e-4 ? nl / m.neckLen : 1;   // (as big as the neck is now: a cub's, a grown lion's)
        M.makeBasis(X.multiplyScalar(s), Y.multiplyScalar(s), Z.multiplyScalar(s)).setPosition(C);
        k.mesh.setMatrixAt(k.n++, M);
      }
      for (const k of kinds.values()) setCount(k.mesh, k.n);
    },
    dispose() {
      for (const k of kinds.values()) { scene.remove(k.mesh); k.mesh.geometry.dispose(); k.mesh.dispose(); }
      mat.userData.ramp.dispose(); mat.dispose(); kinds.clear();
    },
  };
}
