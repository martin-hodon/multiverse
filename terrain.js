// The ground, tessellated where it needs it.
//
// It used to be one PlaneGeometry of 400x400 cells over the whole world: 320,000 triangles, by an order of
// magnitude the heaviest geometry in the game, drawn in every pass of the frame and never frustum-culled --
// one mesh that spans the world is always on screen.
//
// The terrain does not need that grid. groundH is a long, smooth swell (its wavelengths run from 145 to 700
// metres) with a few SHARP things cut into it: every building's plot levelled flat with a 2.5m transition, the
// river's 16m groove, the moats, the lake's rim. A uniform grid pays the same price for the empty meadow as
// for the village -- and still samples the village too coarsely.
//
// So the ground is built as TILES, each tessellated to its own error: the height is sampled on a lattice and
// the coarsest subdivision whose bilinear interpolation stays within `tol` metres of the real ground is the
// one used. Open swell ends up with 26-metre cells, a levelled plot or the river with cells under three.
// Tiles are grouped into blocks and each block is one mesh, so three culls the ones behind you -- which the
// single ground mesh never allowed.
//
// TWO THINGS MAKE THE SEAMS INVISIBLE (both in terrain_data.js, where the arithmetic lives).
//   NORMALS COME FROM groundH, not from the triangles. Two tiles at different subdivisions agree exactly
//   along their shared edge, so the shading cannot tell where the LOD changes; computeVertexNormals would
//   have drawn a crease along every tile border.
//   SKIRTS: a coarse tile's edge is a straight chord where its finer neighbour follows the ground, so a crack
//   can open along the join. Every tile hangs a shallow curtain from its border, in the ground's own colour.
//
// The arithmetic is three-free on purpose: terrain_worker.js runs it off the main thread while the world lays
// itself out, and this module only wraps what comes back in meshes.
import * as THREE from "three";
import { buildTerrainData, gradeRGB } from "./terrain_data.js";

// the lawn's colour by elevation, for callers holding a THREE.Color (the old uniform-grid path)
export function gradeColor(h, grade, lo, mid, hi, out) {
  const rgb = gradeRGB(h, { ...grade, lo: lo.getHex(), mid: mid.getHex(), hi: hi.getHex() }, [0, 0, 0]);
  return out.setRGB(rgb[0], rgb[1], rgb[2], THREE.LinearSRGBColorSpace);
}

// one drawn mesh per block of tiles, from arrays built here or in the worker
export function terrainMeshes(blocks, material) {
  const group = new THREE.Group();
  group.name = "terrain";
  for (const b of blocks) {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(b.pos, 3));
    geo.setAttribute("normal", new THREE.BufferAttribute(b.nor, 3));
    geo.setAttribute("color", new THREE.BufferAttribute(b.col, 3));
    geo.setIndex(new THREE.BufferAttribute(b.idx, 1));
    geo.computeBoundingSphere();
    const m = new THREE.Mesh(geo, material);
    m.matrixAutoUpdate = false;
    m.name = b.name ?? "ground";
    m.userData.noMerge = true;   // merge.js would join these back into one mesh and lose the culling again
    group.add(m);
  }
  return group;
}

// the whole thing on this thread (the worker path is in index.html: same data, built elsewhere)
export function buildTerrain({ material, ...opts }) {
  const { blocks, stats } = buildTerrainData(opts);
  const group = terrainMeshes(blocks, material);
  group.userData.terrain = stats;
  return group;
}
