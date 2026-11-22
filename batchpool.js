// BATCHED POOLS: small meshes of many different shapes that share ONE material -- the tools in people's hands, the
// faces -- drawn as one object (three's BatchedMesh). Every object costs three a render-list entry, a bind group and
// a draw on the CPU each frame however small it is (about 16 us here, more in other browsers), and a pool per shape
// was one object per kind: forty kinds of tool in view were forty draws. Batched, the GPU still draws each copy, but
// three walks one object and the copies go as cheap draws inside its pass.
//
//   const pool = batchPool(scene, material, { name })
//   const shape = pool.add(geometry)      // once per shape (geometries alike: the same attributes, indexed)
//   pool.begin(); pool.put(shape, matrix); ...; pool.end()   // each frame: the copies placed, the rest hidden
//   const id = pool.fix(shape, matrix); pool.hide(id)        // or copies placed once that stay (the meadow's flowers)
//
// It grows as shapes and copies come (doubling its room), and is hidden while it has nothing to draw. GROWING BUILDS A
// NEW ONE (2026-10-23): three's own resizing (setInstanceCount, setGeometrySize) left the WebGPU draw on what it had
// before -- the copies it drew then, where they were then, and nothing added since -- so once more faces came near than
// there was room for, every head stayed behind, piled where they had been, and the people walked on without them. Now
// a pool that must grow makes a fresh BatchedMesh twice the size, adds every shape and copy again in the same order (the
// same ids, so the shapes and copies handed out stay good), and takes the old one's place.
//
// THE OLD ONE IS RETIRED, NOT DISPOSED AT ONCE (2026-11-18): other lists than the scene graph hold objects -- the grass
// mask's flat lists (grass.js), re-gathered twice a second -- and a BatchedMesh disposed while one still held it was
// rendered with its matrices texture gone ("Cannot read properties of null (reading 'image')", every frame until the
// lists caught up). So it is hidden now (three draws nothing hidden, wherever it is listed) and disposed a while later.
import * as THREE from "three";

const RETIRE_MS = 3000;   // (long after every list that might hold the old mesh has been gathered again)
function retire(old) {
  old.visible = false;
  setTimeout(() => old.dispose(), RETIRE_MS);
}

// (verts, indices: the room it starts with -- heads.js's far heads, which come in their hundreds while the world runs,
//  start large rather than grow, a new mesh each time, in the middle of a walk)
// (setup: called on each BatchedMesh made, the first and every bigger one -- bodies.js turns off per-copy culling and sorting)
export function batchPool(scene, material, { name = "batch pool", copies = 16, verts = 2048, indices = 4096, setup = null } = {}) {
  let maxI = copies, maxV = verts, maxX = indices, usedV = 0, usedX = 0;
  const shapes = [], geos = [], copyOf = [];   // the shapes; each one's geometry; each copy's shape -- in the order added
  const make = () => {
    const m = new THREE.BatchedMesh(maxI, maxV, maxX, material);
    m.name = name; m.frustumCulled = false;   // (its copies roam: each culled on its own, perObjectFrustumCulled)
    m.userData.noMerge = true; m.visible = false; m.userData.geos = geos;   // (its shapes, by index: architecture.js itemBudget)
    setup?.(m);
    return m;
  };
  let mesh = make();
  scene.add(mesh);
  const _m = new THREE.Matrix4();
  // room for v more vertices, x more indices and i more copies: if there is not, a new mesh twice the size, all in it again
  const room = (v, x, i) => {
    if (usedV + v <= maxV && usedX + x <= maxX && copyOf.length + i <= maxI) return;
    while (usedV + v > maxV || usedX + x > maxX) { maxV *= 2; maxX *= 2; }
    while (copyOf.length + i > maxI) maxI *= 2;
    const old = mesh, parent = old.parent;
    mesh = make();
    for (const g of geos) mesh.addGeometry(g);
    copyOf.forEach((s, id) => {
      mesh.addInstance(s.id);
      mesh.setMatrixAt(id, old.getMatrixAt(id, _m)); mesh.setVisibleAt(id, old.getVisibleAt(id));
    });
    mesh.visible = old.visible;
    parent?.add(mesh); parent?.remove(old);
    retire(old);
  };
  const copy = (s) => { room(0, 0, 1); copyOf.push(s); return mesh.addInstance(s.id); };
  return {
    get mesh() { return mesh; },
    add(geo) {
      const v = geo.attributes.position.count, x = geo.index ? geo.index.count : v;
      room(v, x, 0);
      const s = { id: mesh.addGeometry(geo), ids: [], n: 0 };
      usedV += v; usedX += x;
      shapes.push(s); geos.push(geo);
      return s;
    },
    begin() { for (const s of shapes) s.n = 0; },
    put(s, matrix) {
      if (s.n === s.ids.length) s.ids.push(copy(s));
      const id = s.ids[s.n++];
      mesh.setMatrixAt(id, matrix); mesh.setVisibleAt(id, true);
    },
    fix(s, matrix) {
      const id = copy(s);
      mesh.setMatrixAt(id, matrix); mesh.visible = true;
      return id;
    },
    hide(id) { mesh.setVisibleAt(id, false); },
    end() {
      let any = false;
      for (const s of shapes) {
        for (let k = s.n; k < s.ids.length; k++) mesh.setVisibleAt(s.ids[k], false);
        if (s.n) any = true;
      }
      mesh.visible = any;
    },
    dispose() { mesh.parent?.remove(mesh); retire(mesh); },
  };
}
