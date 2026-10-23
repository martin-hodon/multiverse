// STATIC MERGE: fewer objects for three to walk.
//
// The world ends up with about a thousand small meshes -- every wall, sill, shutter, rail, crate and mug its
// own object -- and three pays for each of them BEFORE any pixel is drawn: a world matrix, a visibility test,
// a frustum test, a render-list entry, a bind group. That price is paid once per scene traversal, and a frame
// here traverses the scene five times (the grass mask's three passes, the occluders' depth, the picture), so
// a thousand objects is five thousand visits a frame whatever the GPU is doing. The performance lab was
// rewritten around the same fact (one instanced draw per kind of banner instead of a mesh apiece).
//
// Instancing is the wrong tool for this world: every part has its own geometry (the buildings are generated,
// not stamped), so there is nothing to repeat. Merging is the right one -- concatenate the geometry of parts
// that share a parent and a material into one mesh.
//
// WHAT MAKES IT SAFE. The building shaders read the LOCAL position and normal (that is where their planks,
// bark, stone courses and window frames live), so baking a mesh's own transform into its vertices would move
// the pattern with it. This merge therefore refuses any part that is not already at identity -- and in this
// world 758 of 923 parts are, because the generators write their vertices in place. For those the merge is a
// plain concatenation: every attribute copied verbatim, nothing transformed, the picture identical by
// construction (the probe checks it: docs/engines.md).
//
// It also refuses anything that might move on its own (userData.moves / noMerge), anything with children
// hanging off it, multi-material meshes, morph targets, instanced geometry and interleaved attributes.
import * as THREE from "three";

const ID = new THREE.Matrix4().elements;
const identical = (m) => {
  const e = m.elements;
  for (let i = 0; i < 16; i++) if (Math.abs(e[i] - ID[i]) > 1e-9) return false;
  return true;
};
const interleaved = (g) => {
  for (const name of Object.keys(g.attributes)) if (g.attributes[name].isInterleavedBufferAttribute) return true;
  return false;
};

// everything that has to match before two parts may share one mesh: not just the material, but every piece of
// per-object state the renderer or the engines read (layers decide what the grass mask draws, renderOrder
// decides when, userData carries the flags that markGroundProp and the LOD look at)
function signature(o) {
  const g = o.geometry;
  const attrs = Object.keys(g.attributes).sort()
    .map((k) => `${k}:${g.attributes[k].itemSize}:${g.attributes[k].array.constructor.name}`).join(",");
  let ud = "{}";
  try { ud = JSON.stringify(o.userData ?? {}); } catch { return null; }   // a live reference in userData: leave it alone
  return [o.material.uuid, o.layers.mask, o.renderOrder, o.frustumCulled, !!g.index, attrs, ud].join("|");
}

function concat(list) {   // geometries with the same attributes, all already in the parent's space
  const out = new THREE.BufferGeometry();
  let verts = 0, indices = 0;
  for (const g of list) {
    verts += g.attributes.position.count;
    indices += g.index ? g.index.count : g.attributes.position.count;
  }
  for (const name of Object.keys(list[0].attributes)) {
    const first = list[0].attributes[name];
    const arr = new first.array.constructor(verts * first.itemSize);
    let off = 0;
    for (const g of list) {
      const a = g.attributes[name];
      arr.set(a.array.subarray(0, a.count * a.itemSize), off);
      off += a.count * a.itemSize;
    }
    out.setAttribute(name, new THREE.BufferAttribute(arr, first.itemSize, first.normalized));
  }
  const idx = verts > 65535 ? new Uint32Array(indices) : new Uint16Array(indices);
  let io = 0, base = 0;
  for (const g of list) {
    const n = g.attributes.position.count;
    if (g.index) { for (let i = 0; i < g.index.count; i++) idx[io++] = g.index.getX(i) + base; }
    else { for (let i = 0; i < n; i++) idx[io++] = i + base; }
    base += n;
  }
  out.setIndex(new THREE.BufferAttribute(idx, 1));
  return out;
}

// Merge within each parent, never across one: a cart, a windmill or a door group keeps its own transform and
// still moves as a whole, and only the parts inside it are joined.
export function mergeStatic(root, { minGroup = 2 } = {}) {
  // THE MATRICES FIRST. `o.matrix` is only recomputed when three walks the graph to render, and this runs before the
  // first frame -- so a mesh that was given a position and added straight to the scene still had the IDENTITY in its
  // matrix here, passed the "it must be at identity" test below, and had its geometry concatenated verbatim: it ended
  // up at the world's origin. That is where the fountain's water went (a pool and a jet, 97 m from where they belong).
  root.updateMatrixWorld(true);
  const stats = { groups: 0, before: 0, after: 0, refused: 0 };
  const walk = (node) => {
    for (const child of node.children.slice()) if (child.children.length) walk(child);
    const buckets = new Map();
    for (const o of node.children) {
      if (!o.isMesh || o.isInstancedMesh || o.isSkinnedMesh) continue;
      stats.before++;
      const g = o.geometry;
      if (o.children.length || !o.visible || Array.isArray(o.material) || !o.material || !g ||
          o.userData?.moves || o.userData?.noMerge || g.isInstancedBufferGeometry ||
          (g.morphAttributes && Object.keys(g.morphAttributes).length) || !g.attributes?.position ||
          interleaved(g) || (g.groups && g.groups.length > 1) || !identical(o.matrix)) { stats.refused++; continue; }
      const key = signature(o);
      if (key === null) { stats.refused++; continue; }
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push(o);
    }
    for (const group of buckets.values()) {
      if (group.length < minGroup) continue;
      const m = new THREE.Mesh(concat(group.map((o) => o.geometry)), group[0].material);
      m.layers.mask = group[0].layers.mask;
      m.renderOrder = group[0].renderOrder;
      m.frustumCulled = group[0].frustumCulled;
      m.userData = { ...group[0].userData, merged: group.length };
      m.name = `${group[0].name || node.name || "part"}+${group.length}`;
      m.matrixAutoUpdate = false;          // it never moves: it IS the parent's space
      for (const o of group) node.remove(o);
      node.add(m);
      stats.groups++;
    }
  };
  walk(root);
  root.traverse((o) => { if (o.isMesh && !o.isInstancedMesh) stats.after++; });
  return stats;
}

// ACROSS PARENTS: whole streets into one mesh.
//
// mergeStatic stops at each parent, and a building IS a parent -- so after it a village is still a few hundred
// meshes: every house's walls, every house's roof. But a house never moves, and its group differs from the next
// house's by a TRANSLATION alone. So for the groups the world vouches for (`groups`: placed by translation, never
// moved, never hidden, referenced by nobody), parts that share a material are joined across buildings, with each
// building's translation baked into the vertices.
//   The pattern problem (see the top of this file) is solved rather than dodged: `variant(material)` returns the
// material's twin that reads the pattern frame from an `aLocal` attribute -- the vertex's ORIGINAL local position,
// copied verbatim -- so what reaches the pattern is bit for bit what reached it before. A material without a twin
// (variant returns null) does not read the local frame, and is merged plainly.
//   One mesh for the whole world would never be culled, so the joining is per `cell` metres of ground: what is
// behind you still costs nothing.
const _t = new THREE.Vector3(), _q = new THREE.Quaternion(), _s = new THREE.Vector3();
// (a building's meshes may sit a level or two down -- a finished building is a group of one mesh per rule, moved by
//  the offset that centres it on its site -- and are taken from under any group that is only TRANSLATED: each comes
//  with the offset its groups add up to)
const _t2 = new THREE.Vector3(), _q2 = new THREE.Quaternion(), _s2 = new THREE.Vector3();
const meshesUnder = (root, off, out = []) => {
  for (const o of root.children) {
    if (o.isMesh) { out.push({ o, off }); continue; }
    if (!o.children.length || !o.visible || o.userData?.moves || o.userData?.noMerge) continue;
    o.updateMatrix(); o.matrix.decompose(_t2, _q2, _s2);
    if (Math.abs(_q2.w) < 1 - 1e-9 || Math.abs(_s2.x - 1) + Math.abs(_s2.y - 1) + Math.abs(_s2.z - 1) > 1e-9) continue;
    meshesUnder(o, off.clone().add(_t2), out);
  }
  return out;
};
const prune = (root) => { for (const o of [...root.children]) if (!o.isMesh && o.children.length) { prune(o); if (!o.children.length) root.remove(o); } };   // (the groups this emptied)
export function mergeAcross(scene, groups, { cell = 96, variant = () => null } = {}) {
  scene.updateMatrixWorld(true);      // (as above: a stale matrix reads as identity and the part is baked at the origin)
  const stats = { before: 0, after: 0, groups: 0 };
  const buckets = new Map();
  for (const grp of groups) {
    if (grp.parent !== scene) continue;
    grp.updateMatrix(); grp.matrix.decompose(_t, _q, _s);
    if (Math.abs(_q.w) < 1 - 1e-9 || Math.abs(_s.x - 1) + Math.abs(_s.y - 1) + Math.abs(_s.z - 1) > 1e-9) continue;   // translation alone
    const cx = Math.floor(_t.x / cell), cz = Math.floor(_t.z / cell), at = _t.clone();
    for (const { o, off } of meshesUnder(grp, new THREE.Vector3())) {
      if (!o.isMesh || o.isInstancedMesh || o.isSkinnedMesh) continue;
      const g = o.geometry;
      if (o.children.length || !o.visible || Array.isArray(o.material) || !o.material || !g || o.userData?.moves || o.userData?.noMerge ||
          g.isInstancedBufferGeometry || (g.morphAttributes && Object.keys(g.morphAttributes).length) || !g.attributes?.position ||
          interleaved(g) || (g.groups && g.groups.length > 1) || !identical(o.matrix)) continue;
      const sig = signature(o); if (sig === null) continue;
      const key = `${sig}|${cx},${cz}`;
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push({ o, grp, at: at.clone().add(off) });
      stats.before++;
    }
  }
  for (const list of buckets.values()) {
    if (list.length < 2) { stats.after += list.length; continue; }
    const first = list[0].o, twin = variant(first.material);
    const geo = concat(list.map((e) => e.o.geometry)), pos = geo.attributes.position;
    if (twin) geo.setAttribute("aLocal", new THREE.BufferAttribute(pos.array.slice(), 3));   // the pattern's frame: the local positions, verbatim
    let v = 0;
    for (const e of list) {
      const n = e.o.geometry.attributes.position.count;
      for (let i = 0; i < n; i++, v++) pos.setXYZ(v, pos.getX(v) + e.at.x, pos.getY(v) + e.at.y, pos.getZ(v) + e.at.z);
    }
    const m = new THREE.Mesh(geo, twin ?? first.material);
    m.layers.mask = first.layers.mask; m.renderOrder = first.renderOrder; m.frustumCulled = first.frustumCulled;
    m.userData = { ...first.userData, merged: list.length, across: true };
    m.name = `${first.name || list[0].grp.name || "part"}x${list.length}`;
    m.matrixAutoUpdate = false;
    for (const e of list) e.o.parent.remove(e.o);
    scene.add(m);
    stats.groups++; stats.after++;
  }
  for (const grp of groups) if (grp.parent === scene) { prune(grp); if (!grp.children.length) scene.remove(grp); }   // an emptied building group is one object fewer to walk
  return stats;
}

