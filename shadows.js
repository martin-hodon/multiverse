// CONTACT SHADOWS: a soft dark patch on the ground under every figure near you -- people, animals, riders -- so they
// stand ON the ground instead of hovering a hair above it. Not the sun's shadow (the world's light has no direction
// to cast one): the shade right under a body, an ellipse along its heading as wide as it spreads over the ground
// (composite.js keeps each drawn figure's lowest point and spread: an._y0, _fx, _fz), darkest at the middle. Only for
// what stands on something: a figure whose lowest point is off the floor under it (a bird in the air, a swimmer) has
// none. The SHADOWS.max nearest within SHADOWS.near metres; one mesh, one draw, placed on the CPU each frame.
//
//   const shadows = createShadows(scene)
//   shadows.update(herds, camera, floorUnder, bodies)   // bodies: [{ body (an Object3D), yaw, halfL, halfW }] -- the carts
//   (and createShadeBlobs, below: the trees' shade)   // herds: composite herds ({ animals }); floorUnder(an, x, z, y): the
//                                               // floor or ground under that point, at or below y
import * as THREE from "three";
import { attribute, float, vec2, smoothstep, step, floor, fract, sin, cos, dot, positionWorld } from "three/tsl";

const SHADE_C = [.06, .07, .05];   // the shade's colour (linear)
export const SHADOWS = { max: 160, near: 60, dark: .6, lift: .1, gap: .6 };   // lift: over its feet (paving and boards stand proud of the floor height a few cm)

// the shade's look, one for both: near-black, darkest in the middle and fading out to the ellipse's edge (`blobK`: how
// strong, per quad). Darkening blends in linear light: it takes ~.6 to read on screen at all
function shadeMaterial(strip = false) {   // strip: a band darkest along one edge (corner y -1) fading to the other (+1) -- a wall's foot
  const C = attribute("corner", "vec2"), K = attribute("blobK", "float");
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });   // (pulled nearer than the roads and paving are: paths.js pulls them by -1, -2)
  // (the shade's near-black; or a patch's own colour -- fallen leaves: `blobT` 1, flecked in leaf-sized cells, each its own shade)
  const T = attribute("blobT", "float");
  // a leaf in each cell of a world grid: its centre jittered in the cell, turned its own way, twice as long as wide; two
  // grids, one offset and finer, so no rows show
  const leafIn = (scale, off) => {
    const q = positionWorld.xz.mul(scale).add(off), cell = floor(q), f = fract(q).sub(.5);
    const h = fract(sin(dot(cell, vec2(12.9898, 78.233))).mul(43758.5453)), h2 = fract(sin(dot(cell, vec2(39.3468, 11.135))).mul(24634.6345));
    const a = h.mul(6.283), c = cos(a), sn = sin(a), d = f.sub(vec2(h2.sub(.5).mul(.4), h.sub(.5).mul(.4)));
    const u = vec2(d.x.mul(c).add(d.y.mul(sn)), d.y.mul(c).sub(d.x.mul(sn))).mul(vec2(1, 2.1));
    return smoothstep(.36, .26, u.length()).mul(step(.3, h2));
  };
  const leaf = leafIn(6, vec2(0, 0)).max(leafIn(8.5, vec2(.37, .71))), h2 = fract(sin(dot(floor(positionWorld.xz.mul(6)), vec2(39.3468, 11.135))).mul(24634.6345));
  mat.colorNode = attribute("blobC", "vec3").mul(T.mul(h2.mul(.7).add(.65).sub(1)).add(1));
  const fall = strip ? float(1).sub(C.y.mul(.5).add(.5)) : smoothstep(1, .5, C.length());
  mat.opacityNode = (strip ? fall.pow(1.4) : fall).mul(K).mul(SHADOWS.dark).mul(T.mul(leaf.mul(1.6).sub(1)).add(1));
  return mat;
}
// n flat quads (an ellipse's box each: `corner` -1..1 across it), their places and strengths to be written
function blobGeometry(n, dynamic) {
  const pos = new Float32Array(n * 12), cr = new Float32Array(n * 8), idx = new Uint32Array(n * 6), k = new Float32Array(n * 4), col = new Float32Array(n * 12);
  for (let i = 0; i < n; i++) {
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? 1 : -1, v & 2 ? 1 : -1], (i * 4 + v) * 2); col.set(SHADE_C, (i * 4 + v) * 3); }   // (blobT 0: plain shade)
    idx.set([i * 4, i * 4 + 3, i * 4 + 1, i * 4, i * 4 + 2, i * 4 + 3], i * 6);
  }
  const g = new THREE.BufferGeometry(), aP = new THREE.BufferAttribute(pos, 3), aK = new THREE.BufferAttribute(k, 1);
  if (dynamic) { aP.setUsage(THREE.DynamicDrawUsage); aK.setUsage(THREE.DynamicDrawUsage); }
  g.setAttribute("position", aP);
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("blobK", aK);
  g.setAttribute("blobC", new THREE.BufferAttribute(col, 3));
  const tex = new Float32Array(n * 4);
  g.setAttribute("blobT", new THREE.BufferAttribute(tex, 1));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  return { g, pos, k, col, tex, aP, aK };
}
// quad i: an ellipse at x, y, z, semi-axes a along (fa, fb) and b across it, strength s
function putBlob(pos, k, i, x, y, z, a, b, fa, fb, s) {
  for (let v = 0; v < 4; v++) {
    const u = v & 1 ? 1 : -1, w = v & 2 ? 1 : -1, o = (i * 4 + v) * 3;
    pos[o] = x + fa * u * a - fb * w * b; pos[o + 1] = y; pos[o + 2] = z + fb * u * a + fa * w * b;
    k[i * 4 + v] = s;
  }
}

// THE SHADE UNDER THE TREES: the same soft patch, round, under each crown -- as wide as the crown reaches (flora.js
// makeTree `crown`), not as dark as under a body (light comes through the leaves). Built once, with the trees
// (index.html buildFlora); one mesh, one draw.
//   const shade = createShadeBlobs(scene, name)
//   shade.set([{ x, y, z, r, s, c, leaves }...])   // r: its radius, s: how strong (0..1), c: its colour (linear; the shade's by
//                                                // default), leaves: flecked like fallen leaves
export function createShadeBlobs(scene, name) {
  let mesh = null;
  return {
    get mesh() { return mesh; },
    set(blobs) {
      if (mesh) { scene.remove(mesh); mesh.geometry.dispose(); }
      const { g, pos, k, col, tex } = blobGeometry(blobs.length, false);
      blobs.forEach((B, i) => { putBlob(pos, k, i, B.x, B.y, B.z, B.r, B.r, 1, 0, B.s); if (B.c) for (let v = 0; v < 4; v++) col.set(B.c, (i * 4 + v) * 3); if (B.leaves) tex.fill(1, i * 4, i * 4 + 4); });
      g.computeBoundingSphere();
      mesh = new THREE.Mesh(g, mat ??= shadeMaterial());
      mesh.name = name; mesh.renderOrder = 1; mesh.userData.noMerge = true;
      scene.add(mesh);
    },
  };
}
let mat = null;

export function createShadows(scene) {
  const N = SHADOWS.max, { g, pos, k, aP, aK } = blobGeometry(N, true);
  const mesh = new THREE.Mesh(g, mat ??= shadeMaterial());
  mesh.name = "contact shadows"; mesh.renderOrder = 1; mesh.userData.noMerge = true;
  mesh.frustumCulled = false;   // (always round you: nothing to cull)
  scene.add(mesh);
  const near = [];
  return {
    mesh,
    update(herds, camera, floorUnder, bodies = []) {
      const cx = camera.position.x, cz = camera.position.z, R2 = SHADOWS.near * SHADOWS.near;
      near.length = 0;
      for (const h of herds) if (h) for (const an of h.animals) {
        if (an.hidden || an._y0 === undefined) continue;   // (not _out: that is the LAST pass's culling -- a reflection's, a mask's -- not your view's)
        const x = an.position.x + an._bo[0], z = an.position.z + an._bo[2], d2 = (x - cx) ** 2 + (z - cz) ** 2;
        if (d2 < R2) near.push(d2, an);
      }
      // the nearest first, if there are more than the pool holds
      let n = near.length / 2;
      if (n > N) {
        const order = Array.from({ length: n }, (_, i) => i).sort((a, b) => near[a * 2] - near[b * 2]).slice(0, N);
        const keep = order.map((i) => [near[i * 2], near[i * 2 + 1]]).flat(); near.length = 0; near.push(...keep); n = N;
      }
      let m = 0;
      for (let i = 0; i < n; i++) {
        const an = near[i * 2 + 1], x = an.position.x + an._bo[0], z = an.position.z + an._bo[2];
        const fy = floorUnder(an, x, z, an._y0 + .3);
        const lift = Math.max(0, an._y0 - fy - .12), up = 1 - lift / SHADOWS.gap;   // (fainter the higher it is off the floor: a child on a swing, a leap)
        if (up <= 0) continue;   // (off the ground: flying, swimming)
        const fa = Math.cos(an.rotY), fb = -Math.sin(an.rotY);   // (its heading on the ground)
        const big = Math.max(an._fx, an._fz), small = Math.min(an._fx, an._fz);
        const a = Math.max(.85, big * 1.3 + .55), b = Math.max(.7, small * 1.3 + .5), y = Math.max(fy, Math.min(an._y0 - .05, fy + .1)) + SHADOWS.lift;   // (the spread is the bones' ends: the body's flesh and clothes and the shade past the feet added on; at its feet: paving and boards stand a little proud of the floor's height)
        const fade = Math.min(1, (SHADOWS.near - Math.sqrt(near[i * 2])) / 10) * up;
        putBlob(pos, k, m++, x, y, z, a, b, fa, fb, fade);
      }
      // ...and the bodies that are not figures (the carts' beds): their own footprint, half-length along the way they face
      for (const B of bodies) {
        if (m >= N) break;
        const p = B.body.position, d = Math.hypot(p.x - cx, p.z - cz);
        if (d > SHADOWS.near || B.body.visible === false) continue;
        const fy = floorUnder(B, p.x, p.z, p.y + .5);
        putBlob(pos, k, m++, p.x, fy + SHADOWS.lift, p.z, B.halfL + .35, B.halfW + .3, Math.cos(B.yaw), -Math.sin(B.yaw), Math.min(1, (SHADOWS.near - d) / 10));
      }
      for (let j = m * 4; j < N * 4; j++) { k[j] = 0; pos[j * 3] = cx; pos[j * 3 + 1] = -1e3; pos[j * 3 + 2] = cz; }   // (the rest of the pool: folded to a point out of sight -- a per-frame draw range is not honoured by the WebGPU backend here)
      mesh.visible = m > 0;
      aP.needsUpdate = aK.needsUpdate = true;
    },
  };
}

// THE SHADE AT THE FOOT OF THE WALLS: a soft dark band round every building where its walls meet the ground -- the
// light the wall keeps off the ground beside it -- WALL_SHADE.width out, darkest at the wall. Built once from the
// buildings' footprints (index.html: rectangles), in pieces no longer than WALL_SHADE.piece so they follow the ground;
// one mesh, one draw.
export const WALL_SHADE = { width: 1.5, piece: 4, strength: 1, lift: .06 };
export function createWallShade(scene, rects, groundH) {
  const quads = [];
  for (const r of rects) {
    const sides = [[r.x0, r.z0, r.x1, r.z0, 0, -1], [r.x1, r.z0, r.x1, r.z1, 1, 0], [r.x1, r.z1, r.x0, r.z1, 0, 1], [r.x0, r.z1, r.x0, r.z0, -1, 0]];
    for (const [ax, az, bx, bz, nx, nz] of sides) {
      const L = Math.hypot(bx - ax, bz - az), n = Math.max(1, Math.ceil(L / WALL_SHADE.piece));
      for (let i = 0; i < n; i++) quads.push([ax + (bx - ax) * i / n, az + (bz - az) * i / n, ax + (bx - ax) * (i + 1) / n, az + (bz - az) * (i + 1) / n, nx, nz]);
    }
  }
  if (!quads.length) return null;
  const { g, pos, k } = blobGeometry(quads.length, false), W = WALL_SHADE.width;
  quads.forEach(([ax, az, bx, bz, nx, nz], i) => {
    const pts = [[ax, az, 0], [bx, bz, 0], [ax + nx * W, az + nz * W, 1], [bx + nx * W, bz + nz * W, 1]];   // (corner order: x -1/+1 along, y -1 at the wall, +1 out)
    pts.forEach(([x, z], v) => { const o = (i * 4 + v) * 3; pos[o] = x; pos[o + 1] = groundH(x, z) + WALL_SHADE.lift; pos[o + 2] = z; k[i * 4 + v] = WALL_SHADE.strength; });
  });
  g.computeBoundingSphere();
  const mesh = new THREE.Mesh(g, shadeMaterial(true));
  mesh.name = "wall shade"; mesh.renderOrder = 1; mesh.userData.noMerge = true;
  scene.add(mesh);
  return mesh;
}
