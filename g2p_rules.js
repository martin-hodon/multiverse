// SPELLING-TO-SOUND RULES: a rule set is plain lines `X=Y`, applied left to right through a written word.
//
//   ch=x            wherever "ch" stands, say x
//   c(e)=s          a c that is FOLLOWED by e says s      -- context goes in brackets and is not consumed
//   (a)ch=x         a ch that FOLLOWS an a
//   (^a)b(e)=b      the b of a word beginning "abe"       -- ^ is the start of the word, $ the end
//   ^kn=n   e$=     anchors may also stand on the letters themselves; an empty right side is a silent letter
//   c([eiy])=s      [..] is "any one of these letters", in a context or in the letters themselves
//   ah=a:           a colon typed on the right side is the length mark: the same as ah=aː
//   # anything      a comment; blank lines are ignored
//
// AT EACH POSITION every rule whose letters and context match is a candidate, and the MOST SPECIFIC one wins:
// the longest X, counting letters, context and anchors alike (a [..] counts as one). Ties go to the rule that
// consumes more letters, then to the one written LATER -- so a correction added below a rule overrides it without
// the rule having to be found and deleted. Its Y is written out and reading continues AFTER the
// letters it consumed -- context is looked at, never eaten. A letter no rule covers is reported, written as "?".
//
// COMPOSITION. The dictionary marks where a word is put together: abbiegen {ab|biegen}, pothole {pot|hole}. With
// `boundaries` on (the default) the joint is part of what the rules read:
//   - no letter or context matches ACROSS a joint unless the rule says so: the bb of ab|biegen is not a doubled
//     letter, the th of pot|hole is not a digraph;
//   - ^ and $ are the edges of a PART as well as of the word, so by default every part is read as a word of its own
//     (German ab|biegen: the b of ab is final, and devoiced);
//   - a rule may name the joint with | and look past it, for the languages where a joint is NOT a word end:
//       d(|)=d          Polish od|bicie: a d before a joint stays d, although d$=t
//       d(|[ptkfsc])=t  ... unless the next part begins voiceless (od|chodzić)
//       (|)s(t)=ʃ       German Bau|stelle (the same as ^s(t)=ʃ, but ONLY at a joint)
//     A | counts for more than an anchor, so x(|)= beats x$= at a joint whichever is written first.
// Turn `boundaries` off to see what the marks are worth: the word is then read as if it had none.
// No engine imports, no DOM.

const tokens = (s, where) => {                           // "a[eiy]b" -> [Set(a), Set(e,i,y), Set(b)]
  const out = [], c = [...s];
  for (let i = 0; i < c.length; i++) {
    if (c[i] === "[") { const j = c.indexOf("]", i); if (j < 0) throw new Error(`"[" without "]" in ${where}`); out.push(new Set(c.slice(i + 1, j))); i = j; }
    else if (c[i] === "^" || c[i] === "$" || c[i] === "(" || c[i] === ")") throw new Error(`"${c[i]}" is out of place in ${where}`);
    else out.push(new Set([c[i]]));
  }
  return out;
};

export function parseRules(text) {
  const rules = [], errors = [];
  text.split("\n").forEach((raw, n) => {
    const line = raw.replace(/(^|\s)#.*$/, "").trim(); if (!line) return;
    const eq = line.indexOf("="); if (eq < 0) { errors.push(`line ${n + 1}: no "=" in "${line}"`); return; }
    let x = line.slice(0, eq).trim().toLowerCase().normalize("NFC"); const y = line.slice(eq + 1).trim().normalize("NFC").replace(/:/g, "ː");   // (a typed colon is the length mark)
    try {
      let left = "", right = "", start = false, end = false;
      let m = x.match(/^\(([^()]*)\)/); if (m) { left = m[1]; x = x.slice(m[0].length); }
      m = x.match(/\(([^()]*)\)$/); if (m) { right = m[1]; x = x.slice(0, -m[0].length); }
      if (left.startsWith("^")) { start = true; left = left.slice(1); } else if (!left && x.startsWith("^")) { start = true; x = x.slice(1); }
      if (right.endsWith("$")) { end = true; right = right.slice(0, -1); } else if (!right && x.endsWith("$")) { end = true; x = x.slice(0, -1); }
      const L = tokens(left, line), T = tokens(x, line), R = tokens(right, line);
      if (!T.length) throw new Error(`nothing to pronounce in "${line}"`);
      const joints = [...L, ...T, ...R].filter((t) => t.size === 1 && t.has("|")).length;
      rules.push({ text: line, n: n + 1, L, T, R, start, end, y, size: L.length + T.length + R.length + (start ? 1 : 0) + (end ? 1 : 0) + joints / 2, used: 0, wrong: 0 });
    } catch (e) { errors.push(`line ${n + 1}: ${e.message}`); }
  });
  const byFirst = new Map();                             // candidates by the first letter they consume
  for (const r of rules) for (const ch of r.T[0]) { if (!byFirst.has(ch)) byFirst.set(ch, []); byFirst.get(ch).push(r); }
  for (const list of byFirst.values()) list.sort((a, b) => b.size - a.size || b.T.length - a.T.length || b.n - a.n);   // most specific first; on a tie, the LATER line
  return { rules, byFirst, errors };
}

function fits(r, w, i) {
  const t = r.T.length, l = r.L.length, rr = r.R.length;
  if (i + t + rr > w.length || i - l < 0) return false;
  for (let k = 0; k < t; k++) if (!r.T[k].has(w[i + k])) return false;
  for (let k = 0; k < l; k++) if (!r.L[k].has(w[i - l + k])) return false;
  for (let k = 0; k < rr; k++) if (!r.R[k].has(w[i + t + k])) return false;
  return (!r.start || i - l === 0 || w[i - l - 1] === "|") && (!r.end || i + t + rr === w.length || w[i + t + rr] === "|");
}
export function pronounce(set, word, { boundaries = true } = {}) {
  const used = [], missing = []; let out = "";
  const w = [...(boundaries ? word : word.replace(/\|/g, "")).toLowerCase().normalize("NFC")];
  for (let i = 0; i < w.length;) {
    const r = (set.byFirst.get(w[i]) ?? []).find((c) => fits(c, w, i));
    if (!r) { if (w[i] !== "|") { missing.push(w[i]); out += "?"; } i++; continue; }     // (a joint no rule consumes says nothing)
    out += r.y; used.push(r); i += r.T.length;
  }
  return { out, used, missing };
}

// ---- testing a rule set against a word list ---------------------------------------------------------------------------
// lines "word {wo|rd} [ipa]" (the braces are optional); the same spelling may appear with several pronunciations
export function parseWords(text) {
  const by = new Map();
  for (const line of text.split("\n")) {
    const m = line.match(/^(\S+)(?: \{([^}]*)\})? \[([^\]]+)\]$/); if (!m) continue;
    if (!by.has(m[1])) by.set(m[1], { seg: m[2] && m[2].replace(/\|/g, "") === m[1] ? m[2] : m[1], ipas: [] });
    by.get(m[1]).ipas.push(m[3]);
  }
  return by;
}
const UNITS2 = ["aɪ", "aʊ", "eɪ", "oʊ", "ɔɪ", "ɔʏ", "tʃ", "dʒ", "ts", "tɕ", "dʑ", "tʂ", "dʐ", "dz", "pf"], MARKS = "ːʲʰ̃";
const sounds = (s) => { const c = [...s], out = []; for (let i = 0; i < c.length;) { let p = UNITS2.includes(c[i] + (c[i + 1] ?? "")) ? c[i] + c[i + 1] : c[i]; i += [...p].length; while (i < c.length && MARKS.includes(c[i])) p += c[i++]; out.push(p); } return out; };
function distance(a, b) {                                // how many sounds must change
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i, ...new Array(b.length).fill(0)]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[a.length][b.length];
}
export function runTest(set, words, { stress = false, length = true, boundaries = true } = {}) {
  const norm = (s) => { let t = s.normalize("NFC").replace(/g/g, "ɡ"); if (!stress) t = t.replace(/ˈ/g, ""); if (!length) t = t.replace(/ː/g, ""); return t; };
  for (const r of set.rules) { r.used = 0; r.wrong = 0; }
  const misses = [], missing = new Map(); let ok = 0, n = 0, soundsTotal = 0, soundsWrong = 0;
  for (const [word, { seg, ipas }] of words) {
    n++;
    const res = pronounce(set, seg, { boundaries }), got = norm(res.out), want = ipas.map(norm), hit = want.includes(got);
    for (const r of res.used) { r.used++; if (!hit) r.wrong++; }
    for (const ch of res.missing) missing.set(ch, (missing.get(ch) ?? 0) + 1);
    const gs = sounds(got), best = want.map((w) => [distance(gs, sounds(w)), w]).sort((a, b) => a[0] - b[0])[0];
    soundsTotal += Math.max(gs.length, sounds(best[1]).length); soundsWrong += best[0];
    // (gotN / nearN are the forms that were actually compared -- stress and length removed if they are being ignored --
    // so that a display of the difference points at the difference that counted)
    if (hit) ok++; else misses.push({ word, seg, want: ipas.join(" / "), got: res.out, gotN: got, nearN: best[1], off: best[0], rules: res.used.map((r) => r.text) });
  }
  return { n, ok, misses, missing, soundAccuracy: 1 - soundsWrong / Math.max(1, soundsTotal) };
}
