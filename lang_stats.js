// SPELLING -> SOUND STATISTICS over the dictionary in lang/: how each language pronounces each letter and letter
// combination, and where in the word the stress falls. No engine imports, no DOM.
//
// THE PROBLEM is alignment: the dictionary says `church [tʃɜːɹtʃ]`, not which letters made which sounds. It is
// solved the way grapheme-to-phoneme aligners do it:
//   1. the written word is cut into UNITS -- single letters, plus the combinations a language is known to write
//      as one (sch, ch, eau, gn, sz...) and any doubled letter. Longest match first. Where the dictionary marks a
//      word as COMPOSED (ab|biegen), each part is cut on its own and "the start / end of the word" means the part's.
//   2. the pronunciation is cut into PHONEMES -- a symbol with its marks (ː ʲ ʰ and the nasal tilde), affricates
//      and the engine's diphthongs as one each. The stress mark is taken out and remembered.
//   3. every unit is aligned to 0, 1 or 2 phonemes (0 = a silent letter, 2 = x -> ks, ю -> ju; 3 for long units) by VITERBI
//      TRAINING: start from a guess (a letter probably makes the sound that looks like it, vowels make vowels,
//      and things line up roughly left to right), find the best alignment of every word under the current
//      probabilities, recount, repeat. A dozen rounds settle it.
// What comes out is counted: P(sound | unit). It is a statistic of THIS dictionary's transcriptions, which were
// machine-made and then checked for form, not for every vowel -- read it as "how this language usually spells
// its sounds", not as a pronouncing dictionary's verdict on any one word.

export const LANGS = [
  { code: "en", name: "English", col: 0 }, { code: "de", name: "German", col: 1 }, { code: "es", name: "Spanish", col: 2 },
  { code: "fr", name: "French", col: 3 }, { code: "it", name: "Italian", col: 4 }, { code: "ru", name: "Russian", col: 5 },
  { code: "pl", name: "Polish", col: 6 },
];
export const FILES = {
  abstract: ["quantity-number", "space-position", "time", "shape-form", "quality-property", "relation-change"],
  "natural-world": ["sky-celestial", "weather-climate", "water", "land-terrain", "matter-energy"],
  life: ["plants", "animals", "body", "life-processes", "body-actions"],
  cognitive: ["perception", "emotion", "mind-thought", "will-character"],
  humans: ["food-cooking", "agriculture", "clothing", "home-dwelling", "settlement-city", "transport-travel", "technology", "work-industry", "trade-money",
           "society-law-politics", "war-military", "religion-custom", "language-communication", "knowledge-education", "art-entertainment", "family-social", "health-medicine"],
};

// the combinations each language writes as one sound (or one decision). Doubled letters are added automatically.
const COMBOS = {
  en: ["eigh", "ough", "augh", "tion", "sion", "tch", "dge", "igh", "ee", "ea", "oo", "ou", "ow", "ai", "ay", "oi", "oy", "au", "aw", "ie", "ei", "ey", "oa", "ue", "ui", "ew", "eu",
       "th", "sh", "ch", "ck", "ph", "gh", "ng", "wh", "qu", "wr", "kn", "gn", "mb", "sc"],
  de: ["tsch", "sch", "ieh", "ch", "ck", "ph", "pf", "qu", "th", "dt", "tz", "ng", "sp", "st", "ie", "ei", "ai", "eu", "äu", "au", "ah", "eh", "ih", "oh", "uh", "äh", "öh", "üh", "er"],
  es: ["ch", "ll", "rr", "qu", "gu", "gü"],
  fr: ["eaux", "eau", "œu", "oeu", "ain", "aim", "ein", "oin", "ien", "ill", "ou", "oi", "ai", "ei", "au", "eu", "an", "am", "en", "em", "in", "im", "on", "om", "un", "um",
       "ch", "gn", "ph", "qu", "gu", "th", "er", "ez"],
  it: ["gli", "sci", "gn", "sc", "ch", "gh", "ci", "gi", "qu"],
  ru: ["ться", "тся", "дж", "сч"],
  pl: ["dzi", "dź", "dż", "dz", "ch", "cz", "rz", "sz", "ci", "si", "zi", "ni"],
};
const VOWEL_LETTERS = "aeiouyäöüàâáéèêëíîïóôöúùûüœæąęóаеёиоуыэюяy";
const VOWELS = "iɪeɛæaɑɒɔoʊuəʌɜɐyʏøœɨɤɯ";
const DIPHTHONGS = ["aɪ", "aʊ", "eɪ", "oʊ", "ɔɪ", "ɔʏ"], AFFRICATES = ["tʃ", "dʒ", "ts", "tɕ", "dʑ", "tʂ", "dʐ", "dz", "pf"], MARKS = "ːʲʰ̃";
// what sound a letter "looks like", for the first guess only
const LOOKS = { c: "kstθ", q: "k", x: "kɡsx", j: "jʒxd", y: "jiɪya", w: "wv", v: "vfbβ", z: "zstθʐ", g: "ɡɣxdʒ", h: "hx", r: "ɹrɾʁɐ", s: "szʃʒ", ß: "s", ñ: "ɲ", ç: "s", ł: "w", ń: "ɲ", ś: "ɕ", ź: "ʑ", ć: "t", ż: "ʐ",
  a: "aɑæɐəe", e: "eɛəɪi", i: "iɪaj", o: "oɔəɑʌu", u: "uʊʌyjw", ä: "ɛe", ö: "øœ", ü: "yʏ", é: "e", è: "ɛ", ê: "ɛ", ë: "ɛ", à: "a", â: "ɑa", î: "i", ï: "i", ô: "o", û: "y", ù: "u", œ: "œø", á: "a", í: "i", ó: "ou", ú: "u",
  ą: "ɔ", ę: "ɛ", b: "bpβ", d: "dtð", f: "f", k: "k", l: "lɫʎ", m: "m", n: "nŋɲ", p: "p", t: "tdʃ",
  а: "aɐə", б: "bp", в: "vf", г: "ɡkvx", д: "dt", е: "eɪjɛ", ё: "oj", ж: "ʐʂ", з: "zs", и: "iɪɨ", й: "j", к: "k", л: "lɫ", м: "m", н: "n", о: "oɐə", п: "p", р: "r", с: "sz", т: "t", у: "uʊ", ф: "f", х: "x",
  ц: "t", ч: "t", ш: "ʂ", щ: "ɕ", ы: "ɨ", э: "ɛe", ю: "uj", я: "aɪj", ь: "", ъ: "" };

// ---- cutting words up ----------------------------------------------------------------------------------------------
export function units(word, code) {
  const w = [...word], out = [], combos = COMBOS[code] ?? [];
  for (let i = 0; i < w.length;) {
    let hit = null;
    for (const c of combos) if (w.slice(i, i + [...c].length).join("") === c) { hit = c; break; }     // (lists are longest-first)
    if (!hit && w[i + 1] === w[i] && /\p{L}/u.test(w[i])) hit = w[i] + w[i];                          // a doubled letter
    out.push(hit ?? w[i]); i += hit ? [...hit].length : 1;
  }
  return out;
}
// a COMPOSED word (ab|biegen) is cut part by part: no combination and no doubled letter is formed across a joint,
// and `first` / `last` remember which units stand at the edge of a part, so that a context never reaches across one
export function unitsOf(seg, code) {
  const u = [], first = [], last = [];
  for (const part of seg.split("|")) { const us = units(part, code); us.forEach((x, i) => { u.push(x); first.push(i === 0); last.push(i === us.length - 1); }); }
  return { u, first, last };
}
export function phonemes(ipa) {
  const c = [...ipa.normalize("NFC").replace(/g/g, "ɡ")].filter((ch) => ch !== "ˈ"), out = [];   // (the two g glyphs are one sound)
  for (let i = 0; i < c.length;) {
    const two = (c[i] ?? "") + (c[i + 1] ?? "");
    let p = (DIPHTHONGS.includes(two) || AFFRICATES.includes(two)) ? two : c[i];
    i += [...p].length;
    while (i < c.length && MARKS.includes(c[i])) p += c[i++];
    out.push(p);
  }
  return out;
}
export const isVowelP = (p) => VOWELS.includes([...p][0]);
// where the stress falls: [syllables, index of the stressed one from 1] -- a syllable is a vowel nucleus
export function stressOf(ipa) {
  const at = [...ipa].indexOf("ˈ"); if (at < 0) return null;
  const before = phonemes([...ipa].slice(0, at).join("")).filter(isVowelP).length, all = phonemes(ipa).filter(isVowelP).length;
  return all >= 2 && before < all ? [all, before + 1] : null;
}

// ---- reading the dictionary -------------------------------------------------------------------------------------------
export function pairsFrom(texts) {                     // -> per language: [{ word, ipa }] one per WORD (phrases are split when they match)
  const per = LANGS.map(() => []);
  for (const text of texts) for (const line of text.split("\n")) {
    if (!line.trim() || line.startsWith("#")) continue;
    const fields = line.split(", "); if (fields.length !== 8) continue;
    for (const L of LANGS) {
      const m = fields[L.col].match(/^(.*?)(?: \([^)]*\))?(?: \{([^}]*)\})? \[([^\]]+)\]$/); if (!m) continue;
      const words = (t) => t.toLowerCase().normalize("NFC").replace(/[-‐'’]/g, " ").replace(/\./g, "").split(/\s+/).filter(Boolean);
      const ws = words(m[1]), ss = m[2] ? words(m[2]) : [], ps = m[3].trim().split(/\s+/);
      // (an apostrophe separates like a space, so d'accord [dakɔʁ], don't [doʊnt] count as two words with one
      // pronunciation and are skipped below, rather than being fused into the non-words "daccord", "dont")
      if (ws.length !== ps.length) continue;           // l'eau [lo], sich verbeugen with a dropped word...: not alignable word by word
      // the composition marks are used only if they really are this word with | added
      ws.forEach((w, i) => { if (/^\p{L}+$/u.test(w)) per[L.col].push({ word: w, seg: ss.length === ws.length && ss[i].replace(/\|/g, "") === w ? ss[i] : w, ipa: ps[i] }); });
    }
  }
  return per;
}

// ---- the aligner ---------------------------------------------------------------------------------------------------------
export function align(pairs, code, rounds = 12) {
  const data = pairs.map(({ word, seg, ipa }) => ({ word, seg: seg ?? word, ipa, ...unitsOf(seg ?? word, code), p: phonemes(ipa) })).filter((d) => d.u.length && d.p.length);
  let count = new Map();                               // unit -> Map(chunk -> n)
  const add = (C, u, ch, n) => { let m = C.get(u); if (!m) C.set(u, m = new Map()); m.set(ch, (m.get(ch) ?? 0) + n); };
  // the first guess
  for (const d of data) d.u.forEach((u, i) => {
    const first = [...u][0], looks = LOOKS[first] ?? first, vowelU = VOWEL_LETTERS.includes(first);
    d.p.forEach((p, j) => {
      if (Math.abs((i + .5) / d.u.length - (j + .5) / d.p.length) > .34) return;
      const base = [...p][0], same = looks.includes(base) || [...u].some((ch) => (LOOKS[ch] ?? ch).includes(base));
      add(count, u, p, same ? 3 : vowelU === isVowelP(p) ? (vowelU ? 1 : .3) : .02);
      if (j + 1 < d.p.length) add(count, u, p + " " + d.p[j + 1], same ? .25 : .02);
      if (j + 2 < d.p.length && [...u].length >= 3) add(count, u, p + " " + d.p[j + 1] + " " + d.p[j + 2], same ? .6 : .02);   // tion -> ʃən has to be thinkable
    });
    add(count, u, "", .15);
  });
  const INS = -14, FLOOR = Math.log(1e-7);
  // TWO GENTLE PRIORS, because counting alone has a degenerate solution it likes: call the vowel letter silent and
  // let the consonant before it "make" the vowel (ribbon = r-i-bə-(o)-n). A consonant letter that produces a vowel
  // sound, or a vowel letter that produces a true consonant, pays for it -- glides excepted (u -> ju, я -> ja) and
  // the sonorants that really do go syllabic (bottle, button). Mixed units (er, qu, ti...) are left alone.
  const GLIDE = "jwɥ", kindOf = new Map();
  const kind = (u) => { let k = kindOf.get(u); if (k === undefined) { const l = [...u], v = l.filter((ch) => VOWEL_LETTERS.includes(ch)).length; kindOf.set(u, k = v === l.length ? "V" : v === 0 ? "C" : "M"); } return k; };
  const prior = (u, ch) => {
    if (!ch) return 0;
    const k = kind(u); if (k === "M") return 0;
    let pen = 0;
    for (const p of ch.split(" ")) { const vow = isVowelP(p); if (k === "C" && vow) pen -= "lrnmлрнм".includes([...u][0]) ? 1 : 3; if (k === "V" && !vow && !GLIDE.includes([...p][0])) pen -= 3; }
    return pen;
  };
  const viterbi = (d, logp) => {
    const n = d.u.length, m = d.p.length, best = Array.from({ length: n + 1 }, () => new Float64Array(m + 1).fill(-1e18)), back = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(null));
    best[0][0] = 0;
    for (let i = 0; i <= n; i++) for (let j = 0; j <= m; j++) {
      const s = best[i][j]; if (s < -1e17) continue;
      if (j < m && s + INS > best[i][j + 1]) { best[i][j + 1] = s + INS; back[i][j + 1] = [i, j, null]; }        // a sound with no letter: last resort
      // a unit makes 0, 1 or 2 sounds -- 3 if it is three letters or more (tion -> ʃən, ться -> tsə)
      if (i < n) for (let k = 0, top = [...d.u[i]].length >= 3 ? 3 : 2; k <= top && j + k <= m; k++) {
        const ch = d.p.slice(j, j + k).join(" "), v = s + logp(d.u[i], ch) + prior(d.u[i], ch);
        if (v > best[i + 1][j + k]) { best[i + 1][j + k] = v; back[i + 1][j + k] = [i, j, ch]; }
      }
    }
    const out = []; let i = n, j = m;
    while (i || j) { const b = back[i][j]; if (!b) return null; if (b[2] !== null) out.push([d.u[b[0]], b[2]]); else out.push([null, d.p[b[1]]]); [i, j] = b; }
    return out.reverse();
  };
  for (let r = 0; r < rounds; r++) {
    const tot = new Map(); for (const [u, m] of count) { let t = 0; for (const n of m.values()) t += n; tot.set(u, t); }
    const C = count, logp = (u, ch) => { const n = C.get(u)?.get(ch); return n ? Math.log(n / tot.get(u)) : FLOOR; };
    const next = new Map();
    for (const d of data) { d.a = viterbi(d, logp); if (d.a) for (const [u, ch] of d.a) if (u !== null) add(next, u, ch, 1); }
    for (const [u, m] of next) for (const ch of m.keys()) m.set(ch, m.get(ch) + .01);             // never quite zero: a pairing can come back
    count = next;
  }
  const table = new Map(); let inserted = 0;
  for (const d of data) if (d.a) for (const [u, ch] of d.a) { if (u === null) inserted++; else add(table, u, ch, 1); }
  return { table, words: data.length, inserted, data };
}

// ---- what decides it: context -------------------------------------------------------------------------------------------
// A letter with several pronunciations is often not "mixed" at all, only conditional: c is s before e i y and k
// otherwise. For every unit the aligner saw, each occurrence is filed with its surroundings --
//   next / prev   the unit after and before it (# = the word's edge)
//   shape         what follows, as syllable structure: a vowel, one consonant then a vowel (an OPEN syllable), one
//                 final consonant, two or more consonants or a doubled one (a CLOSED syllable), or the end
//   stress        whether the sound it made is the stressed vowel, the one just before it, or neither
// -- and a context is reported ONLY if knowing it makes the pronunciation clearly more predictable: the share you
// would get right by always guessing the commonest option within each context must beat the plain commonest
// option by ten points. Contexts seen fewer than six times are pooled, so a rule cannot be built out of accidents.
const startsVowel = (u) => VOWEL_LETTERS.includes([...u][0]);
const SILENT_LETTERS = "ьъ";
function shapeAfter(all, i, end) {                     // `end`: one past the last unit of this unit's PART of the word
  const us = all.slice(0, end); let c = 0, j = i + 1;
  for (; j < us.length; j++) { const u = us[j]; if (SILENT_LETTERS.includes(u)) continue; if (startsVowel(u)) break; c += [...u].length === 2 && [...u][0] === [...u][1] ? 2 : 1; }
  if (c === 0) return j >= us.length ? "#" : "V";
  return c >= 2 ? "CC" : j >= us.length ? "C#" : "CV";
}
// (`over` is the first letter PAST a joint, for the unit that stands before one: Polish od|bicie / od|chodzić)
export function observations(data) {
  const by = new Map();
  for (const d of data) {
    if (!d.a) continue;
    const st = stressOf(d.ipa), us = d.a.filter(([u]) => u !== null).map(([u]) => u);
    let vow = 0, k = -1;
    for (const [u, ch] of d.a) {
      const ps = ch ? ch.split(" ") : [], nuclei = ps.filter(isVowelP).length;
      if (u === null) { vow += nuclei; continue; }
      k++;
      let stress = "-";
      if (nuclei) stress = !st ? "one syllable" : (st[1] > vow && st[1] <= vow + nuclei) ? "stressed" : st[1] === vow + nuclei + 1 ? "just before the stress" : "unstressed";
      vow += nuclei;
      let end = k + 1; while (end < us.length && !d.first[end]) end++;
      const shape = shapeAfter(us, k, end);
      const o = { label: ch ? ch.replace(/ /g, "") : "silent", long: ch.includes("ː"), voiced: nuclei > 0,
                  ctx: { next: k === us.length - 1 ? "#" : d.last[k] ? "|" : us[k + 1], prev: k === 0 ? "#" : d.first[k] ? "|" : us[k - 1], over: d.last[k] && k < us.length - 1 ? [...us[k + 1]][0] : "", shape, stress, "stress+shape": stress === "-" ? "-" : stress + "|" + shape } };
      if (!by.has(u)) by.set(u, []); by.get(u).push(o);
    }
  }
  return by;
}
// (stress+shape is the one pair worth asking together: a vowel is long in a STRESSED OPEN syllable, and neither half
// of that says much alone)
const FEATURES = ["next", "prev", "shape", "stress", "stress+shape"];
const SHAPE_WORDS = { "#": "word-final", V: "before a vowel", CV: "in an open syllable", "C#": "before one final consonant", CC: "in a closed syllable" };
// the best single context for predicting `pick(o)` among these observations, or null if none is clearly better
export function bestSplit(obs, pick, { minGain = .10, minBucket = 6, features = FEATURES } = {}) {
  const tally = (list) => { const m = new Map(); for (const o of list) m.set(pick(o), (m.get(pick(o)) ?? 0) + 1); return [...m].sort((a, b) => b[1] - a[1]); };
  const n = obs.length, base = tally(obs)[0][1] / n;
  let best = null;
  for (const f of features) {
    // stress is known only for a letter that made a vowel sound, so it may be asked only where EVERY occurrence did:
    // otherwise "no stress value" is just another way of saying "it was silent", and the rule would be reading the answer
    if (f.startsWith("stress") && obs.some((o) => o.ctx.stress === "-")) continue;
    const buckets = new Map(); for (const o of obs) { const v = o.ctx[f]; if (!buckets.has(v)) buckets.set(v, []); buckets.get(v).push(o); }
    const pooled = new Map(), rare = [];
    for (const [v, list] of buckets) if (list.length < minBucket) rare.push(...list); else pooled.set(v, list);
    if (rare.length) pooled.set("(other)", rare);
    if (pooled.size < 2) continue;
    let right = 0; for (const list of pooled.values()) right += tally(list)[0][1];
    // a many-valued context (the neighbouring letter) gets to explain more by accident: it must earn its keep
    const purity = right / n, handicap = f === "next" || f === "prev" ? .025 : f === "stress+shape" ? .04 : 0;
    if (!best || purity - handicap > best.purity - best.handicap) best = { feature: f, purity, handicap, pooled };
  }
  if (!best || best.purity - base < minGain) return null;
  // contexts that lead to the same outcome are one rule
  const groups = new Map();
  for (const [v, list] of best.pooled) { const t = tally(list), lab = t[0][0]; if (!groups.has(lab)) groups.set(lab, { label: lab, contexts: [], list: [] }); const g = groups.get(lab); g.contexts.push([v, list.length]); g.list.push(...list); }
  const rules = [...groups.values()].map((g) => ({ label: g.label, n: g.list.length, share: g.list.filter((o) => pick(o) === g.label).length / g.list.length,
    second: tally(g.list)[1], contexts: g.contexts.sort((a, b) => b[1] - a[1]).map(([v]) => v) })).sort((a, b) => b.n - a.n);
  return { feature: best.feature, base, purity: best.purity, rules };
}
function ruleText(split, labelWord = (l) => l) {
  const f = split.feature, letters = f === "next" || f === "prev", many = split.rules.length > 1;
  // the biggest group is "otherwise" when spelling it out would be a list of everything else
  const isRest = (r, idx) => many && idx === 0 && (r.contexts.includes("(other)") || r.contexts.length > (letters ? 7 : f === "stress+shape" ? 3 : 99));
  const where = (r, idx) => {
    const cs = r.contexts.filter((c) => c !== "(other)");
    if (isRest(r, idx)) return "otherwise";
    if (!cs.length) return "elsewhere";
    const list = cs.slice(0, 12).map((c) => c === "#" ? (f === "next" ? "the end of the word" : "the start of the word") : c === "|" ? "a joint (`|`)" : "`" + c + "`").join(", ") + (cs.length > 12 ? " …" : "");
    if (f === "stress+shape") {                      // stressed|CV, stressed|# ... -> "stressed: open syllable, word-final"
      const by = new Map(); for (const c of cs) { const [a, b] = c.split("|"); if (!by.has(a)) by.set(a, []); by.get(a).push(SHAPE_WORDS[b]); }
      return [...by].map(([a, bs]) => bs.length >= 5 ? a + " (anywhere)" : `${a} ${bs.join(" or ")}`).join("; ");
    }
    return f === "next" ? "before " + list : f === "prev" ? "after " + list : f === "shape" ? cs.map((c) => SHAPE_WORDS[c]).join(" or ") : cs.join(" / ");
  };
  const order = split.rules.map((r, i) => [r, i]).sort((a, b) => (isRest(a[0], a[1]) ? 1 : 0) - (isRest(b[0], b[1]) ? 1 : 0));   // "otherwise" goes last
  return order.map(([r, i]) => `${where(r, i)} → **${labelWord(r.label)}** ${pct(r.share)}` + (r.second && r.second[1] / r.n > .12 ? ` (${labelWord(r.second[0])} ${pct(r.second[1] / r.n)})` : "")).join("; ");
}
const FEATURE_WORDS = { next: "the letter after it", prev: "the letter before it", shape: "the syllable's shape", stress: "stress", "stress+shape": "stress and the syllable's shape" };
// the mixed units and what (if anything) sorts them out; and the same question asked of length
export function conditional(obsBy, { minN = 30 } = {}) {
  const mixed = [], silent = [], length = [], alwaysLong = [], noRule = [];
  const LETTERS_ONLY = ["next", "prev", "shape"];
  for (const [u, obs] of obsBy) {
    if (obs.length < minN) continue;
    // TWO QUESTIONS, not one. Whether a letter is silent is a fact about spelling (the letters round it); which
    // sound it makes when it does sound may also depend on stress. Asking them together lets the second answer
    // leak into the first.
    const sounded = obs.filter((o) => o.label !== "silent"), quiet = (obs.length - sounded.length) / obs.length;
    if (quiet >= .08 && quiet <= .92) { const sp = bestSplit(obs, (o) => o.label === "silent" ? "silent" : "sounded", { features: LETTERS_ONLY }); if (sp) silent.push({ unit: u, n: obs.length, share: quiet, split: sp }); }
    if (sounded.length >= minN) {
      const tops = new Map(); for (const o of sounded) tops.set(o.label, (tops.get(o.label) ?? 0) + 1);
      const top = [...tops].sort((a, b) => b[1] - a[1]);
      if (top[0][1] / sounded.length < .85) { const sp = bestSplit(sounded, (o) => o.label); if (sp) mixed.push({ unit: u, n: sounded.length, top: top.slice(0, 3).filter(([, v]) => v / sounded.length > .05), split: sp }); }
      // length is asked of the occurrences that made a VOWEL when the unit mostly does (Italian i is often the glide
      // j, and a glide has no stress to ask about); of all sounded ones when it is a consonant
      const vowelish = sounded.filter((o) => o.voiced), L = vowelish.length > sounded.length / 2 ? vowelish : sounded;
      const longShare = L.filter((o) => o.long).length / Math.max(1, L.length);
      if (L.length < minN) { /* too few to say */ }
      else if (longShare >= .92) alwaysLong.push({ unit: u, n: L.length, share: longShare });
      else if (longShare >= .06) { const sp = bestSplit(L, (o) => o.long ? "long" : "short", { minGain: .08 }); (sp ? length : noRule).push({ unit: u, n: L.length, share: longShare, split: sp }); }
    }
  }
  const az = (a, b) => a.unit.localeCompare(b.unit);
  return { mixed: mixed.sort(az), silent: silent.sort(az), length: length.sort(az), alwaysLong: alwaysLong.sort(az), noRule: noRule.sort(az) };
}
export function lengthOverall(obsBy) {
  let v = 0, vl = 0, c = 0, cl = 0; const byStress = new Map();
  for (const obs of obsBy.values()) for (const o of obs) {
    if (o.label === "silent") continue;
    if (o.voiced) { v++; if (o.long) vl++; const b = byStress.get(o.ctx.stress) ?? [0, 0]; b[0]++; if (o.long) b[1]++; byStress.set(o.ctx.stress, b); } else { c++; if (o.long) cl++; }
  }
  return { v, vl, c, cl, byStress };
}

// ---- the report -----------------------------------------------------------------------------------------------------------
export function summarise(table, { min = 8, top = 3, floor = .05 } = {}) {
  const rows = [];
  for (const [u, m] of table) {
    let n = 0; for (const v of m.values()) n += v;
    if (n < min) continue;
    const opts = [...m].sort((a, b) => b[1] - a[1]).filter(([, v]) => v / n > floor).slice(0, top).map(([ch, v]) => [ch === "" ? "silent" : ch.replace(/ /g, ""), v / n]);
    rows.push({ unit: u, n, opts, shown: opts.reduce((s, o) => s + o[1], 0) });
  }
  const single = rows.filter((r) => [...r.unit].length === 1).sort((a, b) => a.unit.localeCompare(b.unit)), combo = rows.filter((r) => [...r.unit].length > 1).sort((a, b) => a.unit.localeCompare(b.unit));
  return { single, combo };
}
export function stressStats(pairs) {
  const bySyl = new Map(), fromEnd = new Map(), fromStart = new Map(); let n = 0;
  for (const { ipa } of pairs) {
    const s = stressOf(ipa); if (!s) continue;
    const [syl, at] = s, e = syl - at + 1; n++;
    const k = Math.min(syl, 5); if (!bySyl.has(k)) bySyl.set(k, { n: 0, at: new Map() });
    const b = bySyl.get(k); b.n++; b.at.set(at, (b.at.get(at) ?? 0) + 1);
    fromEnd.set(Math.min(e, 4), (fromEnd.get(Math.min(e, 4)) ?? 0) + 1); fromStart.set(Math.min(at, 4), (fromStart.get(Math.min(at, 4)) ?? 0) + 1);
  }
  return { n, bySyl, fromEnd, fromStart };
}
const pct = (v) => (100 * v).toFixed(v < .1 ? 1 : 0) + "%";
const ORD = ["", "1st", "2nd", "3rd", "4th+"], END = ["", "last", "2nd from end", "3rd from end", "4th+ from end"];
export function markdown(results) {
  let md = "# How each language pronounces its letters — and where it stresses its words\n\n" +
    "Generated by `../lang_stats.html` from the pronunciations in this folder (Chinese is left out: it is not written with letters). " +
    "For every letter and letter combination: how often it occurs (n, counted in dictionary words) and its three most common pronunciations, " +
    "each only if it accounts for more than 5% of that letter's occurrences. `silent` means the letter made no sound of its own. " +
    "Doubled letters count as one unit. Two symbols together (`ks`, `ju`) mean the letter made both sounds.\n\n" +
    "The alignment of letters to sounds is statistical (see `../lang_stats.js`), and the transcriptions themselves were machine-generated, " +
    "so treat a 3% curiosity with suspicion and a 60/30 split as real.\n\n" +
    "Each language then has two more sections. **What decides the mixed ones** takes the letters that have more than one common pronunciation and asks whether " +
    "something nearby settles it -- the letter after or before, the shape of the syllable that follows, or stress -- and lists a rule only where it makes the " +
    "pronunciation clearly more predictable. **Length** asks the same of the length mark ː: which letters are long, and what decides it.\n\n" +
    "Syllable shapes are read off the spelling: *open* = one consonant and then a vowel follow; *closed* = two or more consonants, or a doubled one, follow; " +
    "*before one final consonant*; *before a vowel*; *word-final*. `→ **x** 90% (y 10%)` gives the commonest outcome in that context and the runner-up if it is above 12%. " +
    "*otherwise* means every other context, and is always listed last.\n\n" +
    "Words the dictionary marks as COMPOSED (`abbiegen {ab|biegen}`) are read part by part: no letter combination is formed across a joint, syllable shapes stop " +
    "at it, and *a joint* appears as a context of its own beside *the start / end of the word* -- German `st` is ʃt after a joint as at the start of a word, " +
    "while a Polish `d` before a joint does not devoice as it does at the end of one.\n";
  for (const r of results) {
    md += `\n## ${r.name}\n\n${r.words} words aligned` + (r.inserted ? ` (${r.inserted} sounds could not be given a letter)` : "") + ".\n\n";
    const tab = (rows, head) => `| ${head} | n | pronounced |\n|---|---:|---|\n` + rows.map((x) => `| \`${x.unit}\` | ${x.n} | ${x.opts.map(([ch, v]) => `${ch} ${pct(v)}`).join(" · ")} |`).join("\n") + "\n";
    md += "### Letters\n\n" + tab(r.sum.single, "letter") + "\n### Combinations\n\n" + tab(r.sum.combo, "letters");
    md += "\n### What decides the mixed ones\n\nOnly letters whose pronunciation becomes clearly more predictable from a context are listed (at least ten points better than always guessing the commonest). " +
          "`x% → y%` is that predictability before and after.\n\n" +
          (r.cond.mixed.length ? r.cond.mixed.map((m) => `- \`${m.unit}\` (${m.top.map(([l, v]) => `${l} ${pct(v / m.n)}`).join(" · ")}) — ${pct(m.split.base)} → ${pct(m.split.purity)} by ${FEATURE_WORDS[m.split.feature]}: ${ruleText(m.split)}.`).join("\n") : "_Nothing: no context sorts out what the tables above leave mixed._") + "\n";
    if (r.cond.silent.length) md += "\n**Silent or not** (asked of the letters round it only; the percentages above are of the times it did sound):\n\n" +
          r.cond.silent.map((m) => `- \`${m.unit}\` silent ${pct(m.share)} — ${pct(m.split.base)} → ${pct(m.split.purity)} by ${FEATURE_WORDS[m.split.feature]}: ${ruleText(m.split)}.`).join("\n") + "\n";
    const LO = r.lengthOverall, st = (k) => LO.byStress.get(k), share = (b) => b ? pct(b[1] / b[0]) : "–";
    md += "\n### Length (ː)\n\n" + `${pct(LO.vl / Math.max(1, LO.v))} of vowel sounds are long (${LO.vl} of ${LO.v}): ${share(st("stressed"))} of stressed ones, ${share(st("unstressed"))} of unstressed ones, ${share(st("one syllable"))} in one-syllable words. ` +
          `${pct(LO.cl / Math.max(1, LO.c))} of consonant sounds are long (${LO.cl} of ${LO.c}).\n\n` +
          (r.cond.alwaysLong.length ? "**Long almost always:** " + r.cond.alwaysLong.map((a) => `\`${a.unit}\` ${pct(a.share)}`).join(" · ") + "\n\n" : "") +
          (r.cond.length.length ? "| letters | n | long | what decides it |\n|---|---:|---:|---|\n" + r.cond.length.map((l) => `| \`${l.unit}\` | ${l.n} | ${pct(l.share)} | ` +
            `${FEATURE_WORDS[l.split.feature]} (${pct(l.split.base)} → ${pct(l.split.purity)}): ${ruleText(l.split)}` + " |").join("\n") + "\n"
           : (r.cond.noRule.length ? "" : "_No letter is sometimes long and sometimes short in this language's transcriptions._\n")) +
          (r.cond.noRule.length ? "\nSometimes long, with nothing nearby that clearly decides it: " + r.cond.noRule.map((l) => `\`${l.unit}\` ${pct(l.share)}`).join(" · ") + "\n" : "");
    md += "\n### Stress\n\n";
    const S = r.stress, dist = (m, names) => [...m].sort((a, b) => a[0] - b[0]).map(([k, v]) => `${names[k]} ${pct(v / S.n)}`).join(" · ");
    md += `${S.n} words of two or more syllables carry a stress mark.\n\n- **counted from the start:** ${dist(S.fromStart, ORD)}\n- **counted from the end:** ${dist(S.fromEnd, END)}\n\n`;
    md += "| syllables | words | stressed syllable (from the start) |\n|---:|---:|---|\n" + [...S.bySyl].sort((a, b) => a[0] - b[0]).map(([k, b]) =>
      `| ${k}${k === 5 ? "+" : ""} | ${b.n} | ${[...b.at].sort((x, y) => x[0] - y[0]).map(([at, v]) => `${at}${["", "st", "nd", "rd"][at] ?? "th"} ${pct(v / b.n)}`).join(" · ")} |`).join("\n") + "\n";
  }
  return md;
}
export async function run(fetchText) {
  const texts = []; for (const [dir, names] of Object.entries(FILES)) for (const n of names) texts.push(await fetchText(`lang/${dir}/${n}.txt`));
  const per = pairsFrom(texts);
  return LANGS.map((L) => {
    const a = align(per[L.col], L.code), obs = observations(a.data);
    return { ...L, words: a.words, inserted: a.inserted, table: a.table, data: a.data, sum: summarise(a.table), stress: stressStats(per[L.col]), cond: conditional(obs), lengthOverall: lengthOverall(obs) };
  });
}
