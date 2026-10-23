// WRITTEN SENTENCE -> IPA for ./speech.js, from the dictionary in lang/.
//
//   Der Hund ist schlecht.  ->  deːɐ ˈhʊnt ɪst ˈʃlɛçt.
//
// Every word is looked up, in this order:
//   1. lang/function-words/<lang>.txt   the closed class (the, der, le, и ...): said as written there, so a one-syllable
//                                       function word stays UNSTRESSED -- that is what makes a sentence not a word list
//   2. lang/words/<lang>.txt            the dictionary's content words; a pronunciation without a stress mark (one
//                                       syllable) is stressed. A spelling with several pronunciations (lead, замок)
//                                       takes the first; write lead/2 for the second.
//   3. lang/rules/<lang>.txt            a word the dictionary does not have -- an inflected form, a name -- is READ by the
//                                       spelling rules (./g2p_rules.js) and stressed where the language usually does.
//                                       These are guesses and are reported as such.
// [ˈaɪ pi ˈeɪ] in square brackets is passed through as IPA. An entry without a vowel (в, w, l') and anything joined by an
// apostrophe is a clitic: said in one piece with its neighbour. Chinese has no spaces: the text is cut by longest match.
// No engine imports, no DOM: give it a function that fetches text.
import { parseRules, parseWords, pronounce } from "./g2p_rules.js";
import { phonemes, isVowelP } from "./lang_stats.js";
import { linksR } from "./lang_british.js";

export const LEXICON_LANGS = ["en", "en-GB", "de", "es", "fr", "it", "ru", "pl", "zh"];
// where a word read by RULES is stressed: the syllable counted from the end (1 = last), or from the start (negative)
const DEFAULT_STRESS = { en: -1, "en-GB": -1, de: -1, es: 2, it: 2, pl: 2, fr: 1, ru: 2 };

const plainList = (text) => { const m = new Map(); for (const line of text.split("\n")) { const x = line.match(/^(\S+) \[([^\]]+)\]$/); if (x) { if (!m.has(x[1])) m.set(x[1], []); m.get(x[1]).push(x[2]); } } return m; };
export async function loadLexicon(lang, fetchText, base = "lang/") {
  const get = async (p) => { try { return await fetchText(base + p); } catch { return ""; } };
  const [func, words, rules] = await Promise.all([get(`function-words/${lang}.txt`), get(`words/${lang}.txt`), lang === "zh" ? "" : get(`rules/${lang}.txt`)]);
  const dict = lang === "zh" ? plainList(words) : new Map([...parseWords(words)].map(([w, v]) => [w, v.ipas]));
  const lex = { lang, func: plainList(func), dict, rules: parseRules(rules), segs: lang === "zh" ? null : parseWords(words), longest: 1 };
  for (const m of [lex.func, lex.dict]) for (const k of m.keys()) lex.longest = Math.max(lex.longest, [...k].length);
  return lex;
}

const hasVowel = (ipa) => phonemes(ipa).some(isVowelP);
function stressAt(ipa, lang) {                           // put ˈ before the vowel the language would usually stress
  if (ipa.includes("ˈ")) return ipa;
  const ps = phonemes(ipa), vs = ps.map((p, i) => isVowelP(p) ? i : -1).filter((i) => i >= 0); if (!vs.length) return ipa;
  const want = DEFAULT_STRESS[lang] ?? -1, at = want < 0 ? vs[Math.min(vs.length, -want) - 1] : vs[Math.max(0, vs.length - want)];
  return ps.slice(0, at).join("") + "ˈ" + ps.slice(at).join("");
}
function lookWord(lex, written) {
  const pick = written.match(/^(.*)\/(\d)$/), w = (pick ? pick[1] : written).toLowerCase().normalize("NFC"), n = pick ? +pick[2] - 1 : 0;
  const f = lex.func.get(w); if (f) return { written, ipa: f[Math.min(n, f.length - 1)], source: "function", options: f };
  const d = lex.dict.get(w); if (d) { const ipa = d[Math.min(n, d.length - 1)]; return { written, ipa: lex.lang === "zh" || ipa.includes("ˈ") ? ipa : stressAt(ipa, "en"), source: "dictionary", options: d }; }
  if (lex.lang === "zh" || !lex.rules.rules.length) return { written, ipa: "", source: "unknown" };
  const r = pronounce(lex.rules, w); if (r.missing.length || !r.out) return { written, ipa: r.out.replace(/\?/g, ""), source: "unknown" };
  return { written, ipa: stressAt(r.out, lex.lang), source: "rules" };
}
// (a dictionary word without a stress mark has one syllable, or is a language that marks none: its first vowel is the one)

// ANNOTATIONS in the written text, for an engine that can act on them ({ marks: true }; without it they are dropped):
//   *word* or *several words*   emphasis          (slow: some words)   a named way of speaking, for as long as the brackets last
//   (some words)                an aside           -- the names are the engine's (tract/planner.js PROSODY.styles); they nest.
// They come out in the IPA exactly as written -- `*bˈæd*`, `(slow: ...)` -- so a line of IPA can carry them too.
export function toIPA(lex, text, { marks = false } = {}) {
  const words = [], out = []; let lead = "";                       // lead: opening marks waiting for the word they stand before
  const push = (ipa, glue) => { if (!ipa) return; if (glue && out.length) out[out.length - 1] += ipa; else { out.push(lead + ipa); lead = ""; } };
  const tail = (t) => { if (t && out.length) out[out.length - 1] += t; };
  let glueNext = false;
  // (British English: a word that ends in a written r says it again when the next word begins with a vowel -- "far away", "here is")
  let linkR = false; const link = (r) => { if (lex.lang === "en-GB" && linkR && r.ipa && isVowelP(phonemes(r.ipa.replace(/^[ˈˌ]/, ""))[0] ?? "") && out.length) out[out.length - 1] += "ɹ"; linkR = lex.lang === "en-GB" && !!r.ipa && linksR(r.written.replace(/\/\d$/, ""), r.ipa); };
  const say = (piece, glue) => { const r = lookWord(lex, piece); link(r); words.push(r); const clitic = r.ipa && !hasVowel(r.ipa); push(r.ipa, glue || glueNext); glueNext = clitic && r.source === "function" && !glue; };   // (l' в w lean on the NEXT word; the t of don't has already leaned on the last)
  text = text.replace(/[，、；：]/g, ", ").replace(/。/g, ". ").replace(/？/g, "? ").replace(/！/g, "! ");
  for (const tok of text.normalize("NFC").trim().split(/\s+/)) {
    if (!tok) continue;
    const opener = tok.match(/^(\*?)\(([\p{L}]+):$/u); if (opener) { if (marks) lead += `${opener[1]}(${opener[2].toLowerCase()}: `; continue; }
    const br = tok.match(/^\[(.+)\]([,.?!;:]*)$/); if (br) { words.push({ written: tok, ipa: br[1], source: "ipa" }); push(br[1], glueNext); glueNext = false; if (br[2]) out[out.length - 1] += br[2].replace(/[;:]/g, ","); continue; }
    const m = tok.match(/^([«»"“”„(¿¡*]*)(.*?)([»"“”)*,.?!;:…]*)$/), core = m[2], mark = m[3].replace(/[»"“”]/g, "").replace(/[;:…]/g, ",").replace(marks ? /^$/ : /[)*]/g, "");
    if (marks) lead += m[1].replace(/[^(*]/g, "");
    if (lex.lang === "zh") {                             // no spaces: the longest entry that matches, character by character
      const c = [...core];
      for (let i = 0; i < c.length;) { let hit = 1; for (let n = Math.min(lex.longest, c.length - i); n >= 1; n--) { const s = c.slice(i, i + n).join(""); if (lex.func.has(s) || lex.dict.has(s)) { hit = n; break; } } say(c.slice(i, i + hit).join(""), false); i += hit; }
    } else core.split(/['’‐-]/).filter(Boolean).forEach((piece, i) => say(piece, i > 0 && /['’]/.test(core)));
    tail(mark); if (/[,.?!]/.test(mark)) linkR = false;
  }
  return { ipa: out.join(" "), words, guessed: words.filter((w) => w.source === "rules").map((w) => w.written), unknown: words.filter((w) => w.source === "unknown").map((w) => w.written) };
}

// the IPA of several sentences, one at a time with its mark (. ? !) -- which is what shapes the melody in speech.js
export function sentences(ipa) {
  const out = [], open = []; let cur = [];
  const flush = (mark) => { const text = cur.join(" ") + ")".repeat(open.length); if (/[^\s()*:]/.test(text.replace(/\([\p{L}]+:/gu, ""))) out.push({ ipa: text.trim(), mark }); cur = open.map((o) => o); };
  for (const tok of ipa.split(/\s+/).filter(Boolean)) {
    const o = tok.match(/^\*?(\((?:[\p{L}]+:)?)/u); if (o) open.push(o[1]);
    const end = tok.match(/^(.*?)([.?!]+)([)*]*)$/), shut = (tok.match(/\)/g) ?? []).length;
    cur.push(end ? end[1] + end[3] : tok); for (let k = 0; k < shut; k++) open.pop();     // (what is still open at a sentence's end is closed there and opened again in the next)
    if (end) flush(end[2].includes("?") ? "?" : end[2].includes("!") ? "!" : ".");
  }
  if (cur.length > open.length) flush(undefined);
  return out;
}

// ---- for a page that speaks: written text -> IPA (lexica are loaded once), then said sentence by sentence ----------------
export const SAMPLES = { en: "The old dog is very bad, but I don't lead the horse to water.", "en-GB": "The old dog is not very fast, but her father is here after all.", de: "Der Hund ist schlecht, aber die Sonne scheint über dem Haus.", fr: "L'eau est froide et le chien n'est pas ici.",
  es: "El perro es malo, pero la casa está cerca del río.", it: "Il cane è cattivo, ma c'è una casa vicino al fiume.", ru: "Собака в доме, а вода очень холодная.", pl: "Pies jest w domu, a woda jest bardzo zimna.", zh: "我们的狗很好，你有水吗？" };
const loaded = new Map();
const fetchFile = async (p) => { const r = await fetch(p, { cache: "no-store" }); if (!r.ok) throw new Error(p); return r.text(); };
export async function writtenToIPA(text, lang, fetchText = fetchFile, opts = {}) {
  if (!loaded.has(lang)) loaded.set(lang, await loadLexicon(lang, fetchText));
  return toIPA(loaded.get(lang), text, opts);
}
export function sayResult(speaker, r, lang, mood) {        // synchronous: the engine renders as it is configured at this moment
  lang = lang.split("-")[0];                              // (speech.js knows languages, not accents: en-GB is spoken with its English settings)
  let at; for (const st of sentences(r.ipa)) at = speaker.sayIPA(st.ipa, lang, at === undefined ? undefined : at + .25, mood, st.mark);
  return at;
}
const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;");
export const reportHTML = (r) => `<b>[${esc(r.ipa)}]</b>` +
  (r.guessed.length ? ` &nbsp; <span style="color:#a60">read by the spelling rules (a guess): ${esc(r.guessed.join(", "))}</span>` : "") +
  r.words.filter((w) => (w.options?.length ?? 0) > 1).map((w) => ` &nbsp; <span style="color:#666">${esc(w.written)}: ${w.options.map((o, i) => `/${i + 1} ${esc(o)}`).join("  ")}</span>`).join("") +
  (r.unknown.length ? ` &nbsp; <span style="color:#b00">not pronounceable: ${esc(r.unknown.join(", "))}</span>` : "");
