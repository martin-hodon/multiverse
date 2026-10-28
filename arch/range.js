// THE RANGE (a `range` part): a building one bay deep carried along a LINE that folds -- a covered walk on a city
// wall, the arcaded corridors of a bastion, the long gallery of a palace wing, the watari-yagura that run from keep to
// keep round a Japanese castle's court. What is designed is the line and the section; the walls, the walk on its roof
// and the parapet round the walk follow from them, mitred at every fold, and written as the engine's own parts
// (an enclosure, a prism, an enclosure) which assemble.js builds as any other.
//   THE LINE: `path` [[x, z], ...], its middle line, open; `width` across it (a number, or one per segment: a wing
//     that widens where it turns), `height` to the walk, walls `thickness` thick. Walking along the path, `side`
//     ("right", the default, or "left") is the side that looks OUT -- onto the view, the river, the field.
//   ITS FACES: `faces` { out, in, end } give the openings of every outer face, inner face and the two ends -- any
//     openings spec, and best a row that fits (`every`: as many as the face holds at that pitch), since every face of
//     a folded line is a different length. "out:2", "in:0", "end:1" give one segment's or one end's own.
//   THE WALK on its roof: `walk` { t, over } -- a slab t thick, over the walls' faces by `over` -- or false.
//   THE PARAPET round the walk: `parapet` { breast, merlon, t, step, crenel, end } -- a breastwork cut by crenels every
//     `step` (merlon 0: a plain breastwork), clear of each fold by `end` -- with `gaps` [{ seg, side, at, width }]
//     where a stair comes up or a tower stands: segment `seg`'s "out" or "in" side (or "end" 0 / 1), `at` metres from the
//     segment's middle along the path (the parapet's own face, a little longer or shorter at the folds, is matched to it).
//   THE ROOF instead: `roof` { pitch, overhang, ends, shell } -- two slopes along the line, a hip outside every fold and
//     a valley inside it, gabled or hipped at the ends, open under its rafters: a temple's covered corridor (kairo).
//   `solid: true`: no walls round a hollow but one mass on the band -- a parapet, a dyke, a wall too thin to be a room;
//     `walk` and `parapet` then default to none.
import { bandPoints } from "./build.js";
export { bandPoints };

// the same outline moved OUT by `d` on every side, mitred (insetPoints' sign the other way, for an outline of either winding)
const grown = (pts, d) => pts.map((p1, i) => {
  const n = pts.length, p0 = pts[(i + n - 1) % n], p2 = pts[(i + 1) % n];
  const e0 = [p1[0] - p0[0], p1[1] - p0[1]], e1 = [p2[0] - p1[0], p2[1] - p1[1]], l0 = Math.hypot(...e0), l1 = Math.hypot(...e1);
  const n0 = [-e0[1] / l0, e0[0] / l0], n1 = [-e1[1] / l1, e1[0] / l1];         // (outward: the outside is on the right)
  const k = d / (1 + n0[0] * n1[0] + n0[1] * n1[1]);
  return [p1[0] + (n0[0] + n1[0]) * k, p1[1] + (n0[1] + n1[1]) * k];
});

export function rangeDefs(def, P) {
  const path = def.path.map(([x, z]) => [P(x), P(z)]), n = path.length;
  if (n < 2) throw new Error("a range's path needs two points or more");
  const ws = Array.isArray(def.width) ? def.width.map((w) => P(w)) : path.slice(1).map(() => P(def.width));
  if (ws.length !== n - 1) throw new Error(`a range of ${n - 1} segments has ${ws.length} widths`);
  const { pts, segs } = bandPoints(path, ws);
  let area = 0;
  for (let i = 0; i < pts.length; i++) { const [x0, z0] = pts[i], [x1, z1] = pts[(i + 1) % pts.length]; area += x0 * z1 - x1 * z0; }
  if (area > 0) throw new Error("a range's band came out turned inside out -- its path crosses itself");
  const H = P(def.height), t = P(def.thickness, .9), out = (def.side ?? "right") === "right";
  // what each edge of the band is: [kind, segment or end, the edge runs along the walk (+1) or against it (-1)]
  const edges = pts.map((_, k) => k < n - 1 ? [out ? "out" : "in", k, 1] : k === n - 1 ? ["end", 1, 1]
    : k < 2 * n - 1 ? [out ? "in" : "out", 2 * n - 2 - k, -1] : ["end", 0, 1]);
  const F = def.faces ?? {}, specOf = ([kind, i]) => F[`${kind}:${i}`] ?? F[kind] ?? [];
  const defs = {}, place = [[0, 0, 0, 0]];
  if (def.solid) {
    defs.wall = { type: "prism", plan: { points: pts }, height: H, at: place, ...(def.courses ? { courses: def.courses } : {}) };
    if (!def.walk) return defs;
  } else defs.walls = { type: "enclosure", plan: { points: pts }, thickness: t, height: H, glass: false, interior: def.interior ?? true,   // (its walk inside: an interior)
                 faces: Object.fromEntries(edges.map((e, k) => [String(k), specOf(e)])), at: place,
                 ...(def.courses ? { courses: def.courses } : {}) };
  // A ROOF instead of the walk: two slopes over the band, mitred at the folds (build.js bandRoofMesh) -- open under its
  // rafters (`shell`, its thickness) unless `shell: false`
  if (def.roof) {
    const R = def.roof === true ? {} : def.roof;
    if (ws.some((w) => Math.abs(w - ws[0]) > 1e-6)) throw new Error("a roofed range is one width all along");
    defs.roof = { type: "roof", path, width: ws[0], pitch: P(R.pitch, 25), overhang: P(R.overhang, 1.0), ends: R.ends ?? "gable",
                  ...(R.shell === false ? {} : { shell: P(R.shell, .3) }), at: [[0, H, 0, 0]] };
    return defs;
  }
  const W = def.walk === false || (def.solid && !def.walk) ? null : def.walk ?? {}, wt = W ? P(W.t, .5) : 0, over = W ? P(W.over, .25) : 0;
  if (!W) return defs;
  const top = grown(pts, over);
  defs.walk = { type: "prism", plan: { points: top }, height: wt, walked: true, at: [[0, H, 0, 0]] };
  if (def.parapet === false) return defs;
  // THE PARAPET on the walk's edge: its crenels laid out face by face from the corners in, a gap where a stair arrives
  const pp = def.parapet ?? {}, breast = P(pp.breast, 1.0), merlon = P(pp.merlon, .6), tp = P(pp.t, .45);
  const step = P(pp.step, 2.0), crenel = P(pp.crenel, .7), clear = P(pp.end, tp + .5);
  const gaps = (pp.gaps ?? []).map((g) => ({ seg: Math.round(P(g.seg)), side: g.side ?? "in", at: P(g.at, 0), width: P(g.width, 2.5) }));
  const faces = {};
  top.forEach((p, k) => {
    const q = top[(k + 1) % top.length], L = Math.hypot(q[0] - p[0], q[1] - p[1]), [kind, i, dir] = edges[k];
    // (a gap's place on this face: its point on the path's segment carried square across onto the face's line)
    const e = [(q[0] - p[0]) / L, (q[1] - p[1]) / L], sg = segs[Math.min(i, segs.length - 1)];
    const onFace = (g) => {
      if (kind === "end") return g.at;
      const c = [sg.p[0] + sg.e[0] * (sg.L / 2 + g.at), sg.p[1] + sg.e[1] * (sg.L / 2 + g.at)];
      return (c[0] - p[0]) * e[0] + (c[1] - p[1]) * e[1] - L / 2;
    };
    const gs = gaps.filter((g) => kind === g.side && g.seg === i).map((g) => {
      // (kept on the face, a stub of breastwork at either corner: a gap may not run round a fold)
      const a = onFace(g), lo = Math.max(a - g.width / 2, -L / 2 + tp), hi = Math.min(a + g.width / 2, L / 2 - tp);
      return { at: (lo + hi) / 2, width: hi - lo };
    }).filter((g) => g.width > .3);
    const ops = gs.map((g) => ({ at: g.at, width: g.width, sill: 0, springing: breast + merlon, head: { profile: "flat" } }));
    if (merlon > 0) {
      const m = Math.floor((L - 2 * clear - crenel) / step + 1e-9) + 1;
      for (let j = 0; j < m; j++) {
        const a = (j - (m - 1) / 2) * step;
        if (gs.some((g) => Math.abs(a - g.at) < (g.width + crenel) / 2 + .3)) continue;   // (the gap is there instead)
        ops.push({ at: a, width: crenel, sill: breast, springing: breast + merlon, head: { profile: "flat" } });
      }
    }
    faces[k] = ops;
  });
  defs.parapet = { type: "enclosure", plan: { points: top }, thickness: tp, height: breast + merlon, glass: false, faces, at: [[0, H + wt, 0, 0]] };
  return defs;
}
