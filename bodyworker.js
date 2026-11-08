// THE SCULPTED BODIES' BUILDER, off the main thread (bodies.js hands it a body, bodymesh.js meshes it): a species'
// surface takes a second or more to sample, mesh and simplify -- a herd of species at once would stall the world.
// Three jobs (2026-11-08): `shape` (bodymesh.js buildShape: the surface, meshed and simplified -- the expensive part,
// shared by every coat and variant of that shape), `dress` (dressBody: a body painted on a shape built before, for it or
// for another look of it) and `body` (both at once, as it always was).
import { buildBody, buildShape, dressBody } from "./bodymesh.js";
const arrays = (o) => Object.values(o ?? {}).filter((v) => ArrayBuffer.isView(v)).map((v) => v.buffer);
self.onmessage = ({ data: { id, op = "body", body, shape, family } }) => {
  try {
    if (op === "shape") {
      const S = buildShape(body, { family });
      self.postMessage({ id, B: S }, [...S.lods.flatMap(arrays), ...S.quills.flatMap(arrays)]);
      return;
    }
    const B = op === "dress" ? dressBody(body, shape) : buildBody(body);
    self.postMessage({ id, B }, B.lods.flatMap(arrays));
  } catch (e) { self.postMessage({ id, error: e.stack ?? String(e) }); }
};
