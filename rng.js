// A SEEDED RANDOM STREAM (mulberry32): rng(seed) returns a function giving the next number in [0, 1) -- the same
// seed, the same stream, so a world, a tree or a crowd grows the same every time. Shared by every engine (it lived
// in flora.js until 2026-11-18, which still re-exports it).
export const rng = (seed) => {
  let a = seed | 0;
  return () => {
    a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
};
// (the same stream with a seed of 0 taken as 1 -- as the engines' own copies did, so their creatures and glyphs grow as
//  they always have: bodymesh, hair, items, manes, glyphs)
export const rng1 = (seed) => rng((seed >>> 0) || 1);
// A SMALL LINEAR CONGRUENTIAL STREAM, [0, 1): cheaper and rougher than rng -- what the sea's creatures were placed
// with (pterosaurs, haulout, sealife), kept so they stand where they always stood
export const lcg = (seed) => { let s = (seed >>> 0) || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; };
