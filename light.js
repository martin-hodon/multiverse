// THE WORLD'S LIGHT (2026-10-02): one static sun for everything -- buildings, furniture, tools, figures, flora, the
// ground's key light, the faces -- fixed in the WORLD, so a thing that turns turns its shade with it (a face looking
// toward the sun lights up, looking away falls into shade). Set in config.json `light`:
//   dir      toward the sun, in the world (+y up); normalized here
//   ambient  what a surface facing away from the sun keeps (0 black .. 1 no shading at all)
//   sky      how much of that ambient depends on facing the sky: a shadowed side facing up keeps all of it, one
//            facing the ground (1 - sky) of it -- so form still reads in the shade
// Surfaces are LAMBERT (lightWGSL): ambient + (1 - ambient) * max(0, n . l). Faces are HALF-LAMBERT (heads.js):
// (n . l + 1) / 2 through their own ramp (config.json people.faceShade), which wraps light round the head softly.
// (Constants, not uniforms: the shading functions are spliced into many shaders as text -- edit config.json, reload.)
import * as THREE from "three";
import { wgslFn, normalWorld, faceDirection, vec3 } from "three/tsl";
import CONFIG from "./config.json" with { type: "json" };

const L0 = { dir: [.45, .8, .4], ambient: .62, sky: .2, ...(CONFIG.light ?? {}) };
const len = Math.hypot(...L0.dir) || 1;
export const LIGHT = { ...L0, dir: L0.dir.map((v) => v / len) };

const f = (v) => Number(v).toFixed(5);
// the Lambert term for a WORLD-space unit normal written as WGSL `n` (an expression), as a WGSL f32 expression
export const lightWGSL = (n) => {
  const [x, y, z] = LIGHT.dir, a = LIGHT.ambient, s = LIGHT.sky;
  return `(${f(a)} * (${f(1 - s)} + ${f(s)} * (0.5 + 0.5 * (${n}).y)) + ${f(1 - a)} * max(0.0, dot(${n}, vec3<f32>(${f(x)}, ${f(y)}, ${f(z)}))))`;
};

// A MATERIAL LIT BY THE SUN for geometry that carries its own colours (attribute `color`) and normals: what was
// baked per vertex in the thing's own frame (the arrows) is now shaded in the world's, so it turns with the thing.
// Double-sided ones shade the side that is seen.
const lambert = wgslFn(`fn lambert(n: vec3<f32>) -> f32 { let m = normalize(n); return ${lightWGSL("m")}; }`);
export function litMaterial(opts = {}) {
  const m = new THREE.MeshBasicNodeMaterial({ vertexColors: true, ...opts });
  m.colorNode = vec3(lambert({ n: normalWorld.mul(faceDirection) }));   // (times the vertex colour: vertexColors)
  return m;
}
