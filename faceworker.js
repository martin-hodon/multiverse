// THE FAR HEADS' BUILDER, off the main thread (heads.js "FAR HEADS"): a face takes 25-110 ms to build, and its hollows
// and smoothed normals some 10 ms more -- the far shapes are asked for while the world runs, and each one made on the
// main thread would be a dropped frame or three. heads.js hands it the definitions a face is made of once (`bank`: the
// faces, hairstyles, what is worn, the materials -- the set the face's cache key hashes), then one face at a time as
// buildItem's arguments; it answers with the built face packed as pregen/ keeps one (pregen.js packFace) and, worked
// out over paintedGeometry's layout of it (facecavity.js), its vertices' darkness (`dark`: heads.js cavityOf, with
// `cav`) and its smoothed normals (`sm`: smoothNormals, with `smooth`) -- what heads.js would otherwise work out once
// for the shape -- their buffers transferred.
import { buildItem } from "./items.js";
import { packFace } from "./pregen.js";
import { faceArrays, cavityArrays, smoothArrays } from "./facecavity.js";

let bank = null, lib = {};
self.onmessage = ({ data }) => {
  if (data.bank) { bank = new Map(data.bank); lib = bank.get("items/materials")?.materials ?? {}; return; }
  const { id, path, opts, wet, cav, smooth } = data;
  try {
    const t0 = performance.now(), built = buildItem(path, bank, lib, opts), buf = packFace(built);
    const A = faceArrays(built, { strands: ["hair"], wet }), dark = cavityArrays(A.P, A.N, A.hm, cav), sm = smoothArrays(A.P, A.N, A.hm, A.wm, smooth);
    self.postMessage({ id, buf, dark, sm, ms: performance.now() - t0 }, [buf, dark.buffer, sm.buffer]);
  } catch (e) { self.postMessage({ id, error: e.stack ?? String(e) }); }
};
