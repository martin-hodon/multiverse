// WHAT HANGS ROUND THE NECK (2026-10-06; docs/jewelry.md): every person's necklaces, collars and torcs (jewelry.js
// items) drawn as painted, lit meshes on the CHEST every frame -- as heads.js stands the faces on the heads. A piece is
// built once for its item, its colourway's seed and the FIT it lies on (people.js: the neck's surface as the body and
// its clothes make it), and people of one build in one dress share it: one InstancedMesh a piece-and-fit.
//   The frame is the one the torso is drawn in (shell.js): its origin on the chest's axis at the shoulders' rim (the
// chest part's top end), y up that axis, x the figure's forward (the root's axis, laid square to it), z = x * y.
import * as THREE from "three";
import { setCount } from "./bounds.js";   // (an empty pool not drawn)
import { buildItem } from "./items.js";
import { ASSETS } from "./catalogue.js";
import { paintedGeometry } from "./tools.js";
import { litMaterial } from "./light.js";

const SEEDS = 6;   // (a kind of necklace in so many colourings, by the wearer's seed)
export function createJewels(scene, { cap = 32, bank = ASSETS, lib = bank.get("items/materials")?.materials ?? {} } = {}) {
  const mat = litMaterial(), kinds = new Map();   // key -> { mesh, n } | null
  const clear = () => { for (const k of kinds.values()) if (k) { scene.remove(k.mesh); k.mesh.geometry.dispose(); k.mesh.dispose(); } kinds.clear(); };
  const kindOf = (pc, fit) => {
    const key = `${pc.path}#${pc.seed % SEEDS}|${fit.key}`;
    if (kinds.has(key)) return kinds.get(key);
    let k = null;
    if (bank.has(pc.path)) {
      try {
        const built = buildItem(pc.path, bank, lib, { seed: 1 + (pc.seed % SEEDS), params: { neck: fit } });
        const mesh = new THREE.InstancedMesh(paintedGeometry(built), mat, cap);
        setCount(mesh, 0); mesh.frustumCulled = false; mesh.name = "jewel " + pc.path;
        scene.add(mesh);
        k = { mesh, n: 0 };
      } catch (e) { console.warn(`jewels: ${pc.path}: ${e.message}`); }
    } else console.warn(`jewels: no item "${pc.path}"`);
    kinds.set(key, k);
    return k;
  };
  const M = new THREE.Matrix4(), X = new THREE.Vector3(), Y = new THREE.Vector3(), Z = new THREE.Vector3(), A = new THREE.Vector3(), B = new THREE.Vector3();
  return {
    place(herds) {
      for (const k of kinds.values()) if (k) k.n = 0;
      for (const herd of herds) for (const an of herd.animals) {
        const j = an.jewelry;
        if (!j || an.hidden || an._off || an._out || j.chest < 0 || j.root < 0) continue;
        const [a, b] = herd.ends(an, j.chest), [r0, r1] = herd.ends(an, j.root);
        A.fromArray(a); B.fromArray(b);
        Y.subVectors(A, B).normalize();                                   // up the chest: from the armpits' ring to the rim
        X.fromArray(r1).sub(Z.fromArray(r0)); X.addScaledVector(Y, -X.dot(Y)).normalize();   // the figure's forward, square to it
        if (X.lengthSq() < .5) X.set(Math.cos(an.rotY), 0, -Math.sin(an.rotY));
        Z.crossVectors(X, Y);
        M.makeBasis(X, Y, Z).setPosition(A);
        for (const pc of j.pieces) {
          const k = kindOf(pc, j.fit);
          if (k && k.n < cap) k.mesh.setMatrixAt(k.n++, M);
        }
      }
      for (const k of kinds.values()) if (k) setCount(k.mesh, k.n);
    },
    // (another bank of definitions -- the asset viewer's, its text being edited: every piece made again from it)
    setBank(b) { bank = b; clear(); },
    stats: () => ({ kinds: [...kinds.values()].filter(Boolean).length, shown: [...kinds.values()].reduce((s, k) => s + (k?.n ?? 0), 0) }),
    dispose() { clear(); mat.dispose(); },
  };
}
