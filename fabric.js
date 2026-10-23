// FABRICS FOR THE FIGURES: every cloth a layer of ONE texture array, drawn once from its pattern (patterns.js, the
// family `fabrics`) -- not as a picture in its colours but as the WEIGHTS of its colour slots: red, green and blue
// are how much of slots 1, 2 and 3 a texel is, slot 0 what is left. A garment brings its own four colours (its dyes)
// and the figure engine mixes them by those weights (shell.js), so one layer is every colouring of that cloth, and a
// whole village is dressed from an array of a few dozen small tiles.
//   The tile is RES texels square whatever the pattern's own proportions: the engine is told the pattern's size in
// metres (`periodOf`) and stretches it back. Filtering is the hardware's: a layer is mipmapped on its own and repeats
// on its own, so a check stays a check at a grazing angle and the back seam of a sleeve has no line.
import * as THREE from "three";
import { texture } from "three/tsl";
import { renderPattern, patternOf, sizeOf } from "./patterns.js";
import { PREGEN, pregenOn, pregenMiss, fabricKey, recordFor } from "./pregen.js";   // (build/pregen.py draws them once)

const RES = 128;                               // texels across a layer (a fabric's repeat is 2-30cm: under 2mm a texel)
const SLOTS = 4;                               // colour slots a fabric may use (0-3)
const names = new Map();                       // "fabrics/twill" -> its layer
let cap = 0, data = null, tex = null, node = null;

function makeTex(n) {
  const old = data;
  cap = n; data = new Uint8Array(RES * RES * 4 * n);
  if (old) data.set(old.subarray(0, Math.min(old.length, data.length)));
  const t = new THREE.DataArrayTexture(data, RES, RES, n);
  t.format = THREE.RGBAFormat; t.type = THREE.UnsignedByteType;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.magFilter = THREE.LinearFilter; t.minFilter = THREE.LinearMipmapLinearFilter;
  t.generateMipmaps = true; t.anisotropy = 8;
  t.colorSpace = THREE.NoColorSpace;            // weights, not colours: no sRGB decode
  t.needsUpdate = true;
  tex?.dispose();
  tex = t;
  if (node) node.value = t;
  return t;
}
// the node the shaders read: its value is swapped when the array grows, so a material built once keeps working
export const fabricNode = node = texture(makeTex(16));

// A FABRIC'S LAYER, drawn the first time it is asked for. A pattern's own palette is ignored: each slot is drawn in
// white on black in turn (that slot white, every other black), so the grey of a texel is exactly how much of it that
// slot covers -- anti-aliased edges, a field's blend (a marled wool, a leather's mottle) and all.
export function fabricIndex(ref) {
  if (names.has(ref)) return names.get(ref);
  const def = patternOf(ref);
  if (!def) throw new Error(`no fabric "${ref}"`);
  const i = names.size;
  if (i >= cap) makeTex(cap * 2);
  const off = i * RES * RES * 4;
  const pk = pregenOn() ? fabricKey(ref, RES) : null, cached = pk && PREGEN.fabrics.get(pk);
  if (cached) data.set(cached.getContext("2d", { willReadFrequently: true }).getImageData(0, 0, RES, RES).data, off);
  else {
    for (let q = 0; q < RES * RES; q++) data[off + q * 4 + 3] = 255;
    for (let slot = 1; slot < SLOTS; slot++) {
      const pal = Array.from({ length: SLOTS }, (_, k) => (k === slot ? "#ffffff" : "#000000"));
      const { canvas } = renderPattern(ref, { palette: pal, res: RES });
      const g = canvas.getContext("2d", { willReadFrequently: true });
      // (a pattern that is not square is drawn at its own proportions; it is stretched to the layer's square here)
      let img = g.getImageData(0, 0, canvas.width, canvas.height);
      if (canvas.width !== RES || canvas.height !== RES) {
        const sq = new OffscreenCanvas(RES, RES), sg = sq.getContext("2d", { willReadFrequently: true });
        sg.imageSmoothingQuality = "high";
        sg.drawImage(canvas, 0, 0, RES, RES);
        img = sg.getImageData(0, 0, RES, RES);
      }
      const d = img.data;
      for (let q = 0; q < RES * RES; q++) data[off + q * 4 + slot - 1] = d[q * 4];
    }
    if (pk) pregenMiss("fabric", ref, pk);
    if (pk && PREGEN.record) {   // (the generator keeps the layer as it is stored: a picture of its slot weights)
      const cv = new OffscreenCanvas(RES, RES);
      cv.getContext("2d").putImageData(new ImageData(new Uint8ClampedArray(data.subarray(off, off + RES * RES * 4)), RES, RES), 0, 0);
      recordFor("fabrics", pk, cv);
    }
  }
  tex.needsUpdate = true;
  names.set(ref, i);
  return i;
}

// the fabric's repeat in metres, across and along (the layer is square; the pattern need not be)
export const periodOf = (ref, params) => sizeOf(patternOf(ref), params);
// every fabric drawn so far, for a viewer
export const fabricNames = () => [...names.keys()];
