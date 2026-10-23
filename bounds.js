// BOUNDS FOR GPU-PLACED MESHES. Smoke, flocks, flags, washing, bees... are drawn where their shaders put them, so three
// cannot tell from their vertices where they are -- they used to be drawn every frame, off screen or not
// (frustumCulled false). Here each gets the sphere round the places it can be -- the points it is anchored to (or its
// own vertices, where those are already in place), padded by how far the shader can take it from them -- and three
// skips it, as it does any other mesh, while that sphere is out of view.
//
//   boundTo(mesh, points, pad)   // points: [[x, y, z] | { x, y, z }...], or null for the geometry's own positions
import * as THREE from "three";

export function boundTo(mesh, points, pad = 0) {
  const g = mesh.geometry;
  let s;
  if (points) {
    if (!points.length) return mesh;
    const box = new THREE.Box3(), v = new THREE.Vector3();
    for (const p of points) box.expandByPoint(Array.isArray(p) ? v.set(p[0], p[1], p[2]) : v.set(p.x, p.y, p.z));
    s = box.getBoundingSphere(new THREE.Sphere());
  } else { g.computeBoundingSphere(); s = g.boundingSphere.clone(); }
  s.radius += pad;
  g.boundingSphere = s;
  mesh.frustumCulled = true;
  return mesh;
}

// AN INSTANCED POOL'S COUNT (heads, tools, jewels, manes): how many copies to draw this frame -- and none of it drawn
// while that is 0. three still walks an InstancedMesh with nothing in it through the render list (its bindings, its
// nodes) before it skips the draw: 170 empty pools (a head per face, a tool per kind) cost ~3 ms a frame.
export function setCount(mesh, n) {
  mesh.count = n;
  mesh.visible = n > 0;
  if (n) mesh.instanceMatrix.needsUpdate = true;
}
