// GREEK PAINTINGS, what a solved group looks like (docs/greek.md): pure reads of its pieces, so a panel can be told from another by its shape and not by the names of what's in it.
const COLUMNS = 8;

// a group's outline: how wide for its height, and along eight columns of its width how high it reaches and how far off the ground it starts
export function silhouette(G) {
  let x0 = Infinity, x1 = -Infinity, h = 0;
  const pts = G.pieces.flatMap((p) => p.shaft ? [] : p.rings.flat());
  for (const q of pts) { if (q[0] < x0) x0 = q[0]; if (q[0] > x1) x1 = q[0]; if (q[1] > h) h = q[1]; }
  const span = x1 - x0 || 1, top = new Array(COLUMNS).fill(0), low = new Array(COLUMNS).fill(1);
  for (const q of pts) {
    const i = Math.min(COLUMNS - 1, Math.floor((q[0] - x0) / span * COLUMNS)), y = q[1] / (h || 1);
    if (y > top[i]) top[i] = y;
    if (y < low[i]) low[i] = y;
  }
  return { aspect: span / (h || 1), top, low };
}

// how unlike two outlines are, either way round: a fight mirrored is the same design
export function unlike(a, b) {
  const way = (f) => Math.abs(a.aspect - b.aspect) + a.top.reduce((n, v, i) => n + Math.abs(v - b.top[f(i)]) + Math.abs(a.low[i] - b.low[f(i)]), 0) / a.top.length;
  return Math.min(way((i) => i), way((i) => a.top.length - 1 - i));
}

// how far the skyline dips between its two highest places: nothing, and two bodies read as one mass
export function notch({ top }) {
  let best = 0;
  top.forEach((a, i) => { for (let j = i + 2; j < top.length; j++) best = Math.max(best, Math.min(a, top[j]) - Math.min(...top.slice(i + 1, j))); });
  return best;
}
