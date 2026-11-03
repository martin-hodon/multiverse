// A WINDOW FROM ITS SEED (docs/glass.md, docs/story.md): what a light holds is worked out here, before any glass is cut. A plan in the layer says its subject ({ kind: "story",
// cycle, scene } or { kind: "saint", who } ...); the seed says the rest: which scenes in which order, how the panels are arranged, the border, the diaper, the colours of the ground. Out come plain panels for glass/layout.js.
import { stream, one, shuffled, scramble } from "../story/seed.js";
import { CANON, dyeOf } from "../story/compose.js";

// the palette's slots (assets/patterns/glass.json) by the canon's names
export const DYE = dyeOf({ cobalt: 0, ruby: 1, gold: 2, emerald: 3, white: 4, flesh: 5, purple: 6, sky: 7, amber: 8, navy: 9, brown: 10, rose: 11, olive: 12, grey: 13 });
const NAME = ["cobalt", "ruby", "gold", "emerald", "white", "flesh", "purple", "sky", "amber", "navy", "brown", "rose", "olive", "grey"];
export const tintName = (slot) => NAME[slot];

const BORDERS = [
  { t: .11, fills: [1, 0, 2, 0], pearl: 4, line: 9, block: .16 },
  { t: .09, fills: [0, 1], pearl: 4, line: 2, block: .2 },
  { t: .12, fills: [1, 2, 0, 2], pearl: 4, line: 9, block: .14, motif: "fleur" },
  { t: .12, fills: [0, 1], line: 2, block: .19, motif: "fleur" },
  { t: .12, fills: [1, 0], pearl: 4, line: 3, block: .19, motif: "castle" },
  { t: .1, fills: [3, 1, 3, 2], line: 4, block: .15 },
  { t: .1, fills: [6, 2, 0, 2], pearl: 4, line: 9, block: .15 },
  { t: .08, fills: [2, 1], line: 9, block: .12, motif: "chevron" },
  { t: .125, fills: [3, 0, 1, 0], pearl: 4, line: 2, block: .2, motif: "leaf" },
  { t: .1, fills: [1, 3], line: 2, block: .18, motif: "leaf" },
];
const GROUNDS = [[1, 9], [0, 1], [1, 0], [9, 1], [3, 1], [6, 0], [1, 3]];
const DIAPERS = ["lattice", "lattice", "squares", "damask", "rings"];
const SHAPES = ["circle", "circle", "quatrefoil", "lozenge", "barbed"];

// what the panels stand on, and how each is framed, the same through a window
function style(seed, plan) {
  const r = stream(scramble(seed), "style");
  return { r, border: one(BORDERS, r), ground: one(GROUNDS, r), diaper: one(DIAPERS, r), fleuron: r() < .6 ? one([7, 2, 4], r) : undefined, band: one([2, 2, 4, 3, 1], r), medal: one([0, 0, 0, 1, 9, 7], r), canopy: one([2, 2, 4, 8], r), canopy2: one([4, 2, 13], r), shape: plan.shape ?? one(SHAPES, r), alternate: r() < .35, pearl: r() < .7 ? 4 : undefined };
}
// (a medal's colour, not the colour of what's round it)
const medalOn = (S, i) => { const m = S.alternate && i % 2 ? (S.medal === 1 ? 0 : 1) : S.medal; return m === S.ground[0] ? (m === 1 ? 0 : 1) : m; };
const scenes = (plan, n, r) => {                                         // (a run of the story, told upwards as a window reads; or what the plan names first)
  const list = plan.scenes ?? shuffled(plan.cycles ?? ["infancy", "passion"], r).flatMap((c) => CANON.cycles[c]);
  if (n >= list.length) return list.slice();
  const at = Math.floor(r() * (list.length - n + 1));
  return list.slice(at, at + n);
};
const medal = (S, scene, i, r) => ({ form: "medallion", h: 1, shape: S.alternate && i % 2 ? one(["lozenge", "quatrefoil"], r) : S.shape, scene, ground: medalOn(S, i), band: S.band, r: .46 });
const arcade = (S, scene, i, r, h = 1) => ({ form: "saint", h, scene, ground: i % 2 ? S.ground[0] : S.ground[1], canopy: S.canopy, canopy2: S.canopy2, base: 3, spring: .74, wide: 1, arch: i % 2 ? S.ground[1] : S.ground[0] });

const LAYOUTS = {
  stack(S, plan, tall, r) { const n = tall ? 2 + Math.floor(r() * 2) + (plan.big ? 1 : 0) : 1, list = scenes(plan, n, r); return list.map((q, i) => medal(S, q, i, r)); },
  cluster(S, plan, tall, r) { const n = tall ? 2 : 1, list = scenes(plan, n, r), who = shuffled(["prophet", "apostle", "angel", "apostle-old", "prophet", "angel"], r); return list.map((q, i) => ({ ...medal(S, q, i, r), form: "cluster", shape: "circle", r: .4, busts: who.slice(0, 4) })); },
  registers(S, plan, tall, r) { const n = tall ? 3 : 1, list = scenes(plan, n, r); return list.map((q, i) => arcade(S, q, i, r)); },
  band(S, plan, tall, r) { const [q] = scenes(plan, 1, r), g = { form: "grisaille", h: .9, d: 1 / 6, whites: [4, 4, 13, 4], ...(r() < .5 ? { strap: { n: 1, fill: 4, knot: S.band, knot2: 8 } } : null) }; return tall ? [g, arcade(S, q, 0, r, 1.1), g] : [arcade(S, q, 0, r)]; },
  tree(S) { return [{ form: "jesse", h: 1, ground: S.ground[0], ground2: S.ground[1] }]; },
};
// A LIGHT'S PANELS. -> a layer as layout.js has always read: panels, border, ground, and the new keys (diaper, medal, motif)
export function planLight(L) {
  const P = L.plan, seed = L.seed ?? 1, S = style(seed, P), r = S.r, tall = (L.opening?.h ?? 1) > 2, border = P.border === false ? L.border : L.border?.sides ? L.border : S.border;
  let panels;
  if (P.kind === "saint") {
    const who = P.who ?? one(CANON.standing, r), one_ = { form: "saint", h: 1, person: who, ground: S.ground[0], arch: S.ground[1], canopy: S.canopy, canopy2: S.canopy2, base: 3, spring: .74, donor: r() < .3 && !P.who };
    const kind = r();
    if (!tall) panels = [one_];
    else if (kind < .45) panels = [one_];
    else if (kind < .75) { const [sc] = scenes({ cycles: P.cycles ?? ["infancy", "passion", "lives"] }, 1, r); panels = [{ ...arcade(S, sc, 1, r, .62), spring: .78 }, { ...one_, h: 1 }]; }
    else { const other = one(CANON.standing.filter((n) => n !== who), r); panels = r() < .5 ? [{ ...one_, h: 1 }, { ...one_, person: other, ground: S.ground[1], arch: S.ground[0], h: 1 }] : [{ ...one_, person: other, ground: S.ground[1], arch: S.ground[0], h: 1 }, { ...one_, h: 1 }]; }
  } else if (P.kind === "tree") panels = LAYOUTS.tree(S);
  else if (P.scene) {                                                    // (a named scene: its subject stays, the rest may change)
    const q = { ...P, scenes: tall ? [P.scene, ...scenes(P, 2, r)] : [P.scene] }, kind = tall ? "stack" : one(["stack", "stack", "registers", "cluster"], r);
    panels = kind === "stack" ? q.scenes.map((n, i) => medal(S, n, i, r)) : LAYOUTS[kind](S, q, tall, r);
  } else panels = LAYOUTS[P.layout ?? (tall ? one(["stack", "stack", "stack", "cluster", "cluster", "registers", "registers", "band"], r) : one(["stack", "registers", "cluster"], r))](S, P, tall, r);
  return { ...L, panels, border, ground: S.ground, fleuron: S.fleuron, pearl: S.pearl, diaper: S.diaper };
}

// A ROSE'S PEOPLE (form: "stone"): who stands in the lights, what's in the hub, and the colours
const THEMES = [
  { hub: "pantocrator", lights: ["angel", "peter", "agnes", "bishop", "angel", "paul", "king", "catherine"] },
  { hub: "virgin", lights: ["prophet", "king", "prophet", "david", "prophet", "moses", "king"] },
  { hub: "christ", lights: ["elder"] },
  { hub: "christ", lights: ["peter", "andrew", "james", "john", "matthew", "thomas", "bartholomew", "philip", "simon", "jude", "paul", "apostle"] },
  { hub: "lamb", lights: ["angel", "martyr", "angel", "agnes", "angel", "catherine", "angel", "lucy"] },
  { hub: "virgin", months: true },
  { hub: "pantocrator", lights: ["catherine", "barbara", "margaret", "cecilia", "agnes", "lucy", "ursula", "magdalene"] },
];
export function planRose(L) {
  const r = stream(scramble(L.seed ?? 1), "rose"), T = L.theme ?? one(THEMES, r), scheme = one([[0, 1], [1, 0], [0, 9], [1, 9], [0, 6]], r), roundels = one([[1, 3, 2], [3, 0], [2, 1], [1, 2, 0, 2], [6, 2]], r);
  return { ...L, plan: null, theme: T, fills: scheme, roundel: roundels, ground: one([9, 9, 0], r), hub: one([2, 2, 4, 1], r), medals: one([[0, 1], [1, 0], [0, 0], [1, 1], [9, 1]], r), foils: r() < .5 ? 4 : 6, pearl: r() < .5 ? 4 : 1, offset: Math.floor(r() * 12) };
}

// A ROSE OF RINGS (form: "rose"): the eye, one to three rings of shapes in numbers that go together, the colours; its people in the roundels of one ring. Keeps its palette and a character of its own (`plan.like`)
export function planRings(L) {
  const r = stream(scramble(L.seed ?? 1), "rings"), P = L.plan, n = one(P.like === "paris" ? [12, 12, 16] : [12, 12, 8, 16], r), g = P.like === "paris" ? 9 : one([0, 0, 9, 0], r), eye = .1 + r() * .06, band = (a) => one(a, r);
  const inner = (k, ...f) => ({ k, fills: f });
  const A = band(P.like === "paris" ? ["petal"] : ["round", "petal", "quatrefoil"]), B = band(P.like === "paris" ? ["petal", "petal", "round"] : ["square", "round", "quatrefoil", "petal"]), C = band(["round", "quatrefoil", "round"]), three = r() < .75;
  const f1 = band([[1], [1, 0], [0, 1], [1, 2]]), f2 = band([[1, 2], [1, 0, 6, 0], [2, 1], [3, 1]]), f3 = band([[0, 1], [1, 3], [2, 1], [0, 1, 2, 1]]);
  const m1 = eye + (three ? .3 : .42), m2 = m1 + (three ? .24 : 0), peopled = n <= 12 && r() < .8 ? (three ? 2 : 1) : -1;
  const rings = [{ shape: A, r0: eye, r1: m1, n, fills: f1, ...(A === "petal" ? { gap: .05 } : null), inner: inner(A === "petal" ? .5 : .6, 2, 4) }];
  if (three) rings.push({ shape: B, r0: m1, r1: m2, n: B === "petal" ? n * 2 : n, fills: f2, turn: B === "petal" ? 0 : .5, ...(B === "petal" ? { gap: .04 } : null), inner: inner(.52, 4, 2) });
  rings.push({ shape: C, r0: three ? m2 : m1, r1: .985, n, fills: f3, turn: three ? 0 : .5, inner: inner(peopled >= 0 ? .8 : .55, 2, 3) });
  const back = rings.map((q, i) => ({ shape: "sector", r0: q.r0, r1: i === rings.length - 1 ? 1.02 : rings[i + 1].r0, n: q.n, turn: q.turn ?? 0, fill: g, role: "ground" }));
  const who = one([["angel"], ["prophet", "king"], ["peter", "paul", "andrew", "james", "john", "matthew", "thomas", "philip"], ["catherine", "agnes", "lucy", "cecilia", "barbara", "margaret"], ["elder"]], r);
  return { ...L, plan: null, ground: g, rings: [...back, ...rings, { r1: eye + .005, fill: band([2, 2, 4]) }, ...(r() < .5 ? [{ r1: eye * .55, fill: band([1, 0]) }] : [])], busts: peopled >= 0 ? { ring: peopled, who, seed: L.seed ?? 1 } : null };
}
