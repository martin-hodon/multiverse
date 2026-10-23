// THE NUMBER THAT IS WRITTEN AS A SUM. Every definition in this project -- a building's (assets/architecture), a
// creature's (assets/creatures) -- may write any number as an EXPRESSION over the definition's own params:
// "rOuter - wallT", "0.65 * s", "spring + openW * 0.5". That is what lets one definition stand on another:
// the lower one says what it is in terms of names, the higher one says what those names are.
//
// No eval and no library: names, numbers, + - * / and brackets, and a few functions -- min(a, b, ...), max(...),
// floor(a), ceil(a), round(a), abs(a), atan2(y, x), sin, cos, sqrt -- for a count that must follow the detail level but stay within what the shape
// allows. A name may itself hold an expression (params are resolved as they are reached), so a param may be
// written in terms of another.
const FNS = { min: Math.min, max: Math.max, floor: Math.floor, ceil: Math.ceil, round: Math.round, atan2: Math.atan2, abs: Math.abs, sin: Math.sin, cos: Math.cos, sqrt: Math.sqrt };
export function evalExpr(src, params) {
  let i = 0;
  const ws = () => { while (i < src.length && src[i] === " ") i++; };
  const num = () => {
    ws();
    if (src[i] === "(") { i++; const v = sum(); ws(); if (src[i] !== ")") throw new Error(`missing ) in "${src}"`); i++; return v; }
    if (src[i] === "-") { i++; return -num(); }
    const s = i;
    while (i < src.length && /[A-Za-z0-9_.]/.test(src[i])) i++;
    const tok = src.slice(s, i);
    if (tok === "") throw new Error(`cannot read "${src}" at ${i}`);
    if (/^[0-9.]+$/.test(tok)) return parseFloat(tok);
    ws();
    if (src[i] === "(" && tok in FNS) {
      i++; const args = [sum()];
      for (ws(); src[i] === ","; ws()) { i++; args.push(sum()); }
      if (src[i] !== ")") throw new Error(`missing ) in "${src}"`);
      i++; return FNS[tok](...args);
    }
    if (!(tok in params)) throw new Error(`"${tok}" is not a parameter (in "${src}")`);
    return evalNum(params[tok], params);
  };
  const prod = () => { let v = num(); for (ws(); src[i] === "*" || src[i] === "/"; ws()) { const op = src[i++]; const r = num(); v = op === "*" ? v * r : v / r; } return v; };
  const sum = () => { let v = prod(); for (ws(); src[i] === "+" || src[i] === "-"; ws()) { const op = src[i++]; const r = prod(); v = op === "+" ? v + r : v - r; } return v; };
  const v = sum();
  ws();
  if (i < src.length) throw new Error(`cannot read "${src}" from ${i}`);
  return v;
}
export const evalNum = (v, params) => (typeof v === "number" ? v : evalExpr(String(v), params));
// A PARAMETER MAY BE A WORD, not only a number: "pointed" for the arch profile a whole building is drawn
// with, "slit" for a cat's pupil. Anything that does not read as an expression is kept as it stands, and only
// the places that expect a word ever look at it.
export const evalValue = (v, params) => { try { return evalNum(v, params); } catch (e) { return typeof v === "string" ? v : (() => { throw e; })(); } };
// ...and a whole structure of them: arrays and objects of expressions, resolved in place. `keep` names the
// keys whose values are NOT numbers to be resolved (an id, a pattern, a colour): they are copied as they are.
export function evalDeep(v, params, keep = () => false) {
  if (Array.isArray(v)) return v.map((x) => evalDeep(x, params, keep));
  if (v && typeof v === "object") {
    const out = {};
    for (const k of Object.keys(v)) out[k] = keep(k) ? v[k] : evalDeep(v[k], params, keep);
    return out;
  }
  return evalValue(v, params);
}
