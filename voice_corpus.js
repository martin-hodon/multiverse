// A LABELLED SPEECH CORPUS as something the synthesiser can be held against: voices/spr08 is one woman (34) saying ten
// German sentences neutrally and in five emotions, 16 kHz, every SOUND hand-labelled with its start time (lablaut),
// every syllable too (silb), and each take rated by 20 listeners (evaluation.txt). File names: 08 a01 N a = speaker,
// sentence, emotion (N neutral, W anger, F joy, T sadness, L boredom, A fear), take.
// What this module does: read a take into { samples, phones [{ sampa, t0, t1, accent }], ipa } -- the IPA being the
// sounds she ACTUALLY said (haben as "ham", lenited b and d), spelled for ../speech.js, so that synthesiser and
// recording can be compared sound for sound. No engine imports, no DOM.
import { parseWav } from "./voice_analysis.js";

export const EMOTIONS = { N: "neutral", W: "anger", F: "joy", T: "sadness", L: "boredom", A: "fear" };
export const SPR08 = {
  dir: "voices/spr08",
  files: ["08a01Ab", "08a01Fd", "08a01Lc", "08a01Na", "08a01Wa", "08a01Wc", "08a02Ab", "08a02Ac", "08a02Fe", "08a02La", "08a02Na", "08a02Tb", "08a02Wc", "08a04Ff", "08a04La", "08a04Nc", "08a04Tb", "08a04Wc", "08a05Fe", "08a05Lc", "08a05Nb", "08a05Ta", "08a05Wa", "08a07Fd", "08a07La", "08a07Na", "08a07Ta", "08a07Tb", "08a07Wc", "08b01Aa", "08b01Fd", "08b01Fe", "08b01Lb", "08b01Na", "08b01Wa", "08b02Ff", "08b02La", "08b02Nb", "08b02Tc", "08b02Wd", "08b03Fe", "08b03Lc", "08b03Nb", "08b03Tc", "08b03Wd", "08b09Ab", "08b09Fd", "08b09Lc", "08b09Nb", "08b09Tb", "08b09Wa", "08b09Wc", "08b10Aa", "08b10Fd", "08b10La", "08b10Nc", "08b10Tc", "08b10Wa"],
  // syllables per word, for the word gaps (the syllable labels are orthographic: "der la pen liegt auf dem eis schrank")
  words: { a01: [1, 2, 1, 1, 1, 2], a02: [1, 1, 1, 1, 2, 3], a04: [2, 2, 2, 1, 1, 1, 2], a05: [1, 2, 1, 2, 3, 1, 1, 2, 2, 1, 2], a07: [1, 2, 2, 1, 1, 2, 1],
           b01: [1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2], b02: [1, 2, 1, 3, 4, 1, 1, 2, 1, 2, 2], b03: [1, 1, 4, 1, 1, 1, 2, 1, 2, 3, 1, 2, 2, 2],
           b09: [1, 1, 1, 2, 3, 1, 1, 1, 1, 1, 2, 1], b10: [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3] },
};
export const nameParts = (f) => ({ speaker: f.slice(0, 2), sentence: f.slice(2, 5), emotion: f[5], take: f[6] });

// the corpus's SAMPA -> the engine's IPA. Tense vowels are long when accented; X is the uvular fricative r, 6 the
// vocalised one, B D the lenited b d of fast speech, H a voiced h; the glottal stop has no sound in the engine.
const SAMPA = { a: "a", e: "e", i: "i", o: "o", u: "u", y: "y", "2": "ø", E: "ɛ", I: "ɪ", O: "ɔ", U: "ʊ", Y: "ʏ", "9": "œ", "@": "ə", "6": "ɐ", aI: "aɪ", aU: "aʊ", OY: "ɔʏ", i6: "iɐ",
  p: "p", b: "b", t: "t", d: "d", k: "k", g: "ɡ", f: "f", v: "v", s: "s", z: "z", S: "ʃ", Z: "ʒ", C: "ç", x: "x", X: "ʁ", r: "ʁ", R: "ʁ", h: "h", H: "ɦ", j: "j", l: "l", m: "m", n: "n", N: "ŋ",
  "4": "ɾ", B: "β", D: "ð", G: "ɣ", "?": "" };
const TENSE = "eiouy2";
const STOPS = "pbtdkg";
export const CLASSES = ["vowel", "nasal", "liquid/glide", "voiced fricative", "voiceless fricative", "voiced stop", "voiceless stop"];
export const phoneClass = (s) => "ptk".includes(s) ? "voiceless stop" : "bdg".includes(s) ? "voiced stop" : ["f", "s", "S", "C", "x", "h"].includes(s) ? "voiceless fricative"
  : ["v", "z", "Z", "H", "X", "r", "R"].includes(s) ? "voiced fricative" : ["m", "n", "N"].includes(s) ? "nasal" : ["l", "j", "4", "B", "D", "G"].includes(s) ? "liquid/glide" : s === "?" ? null : "vowel";

// xlabel files: a header up to "#", then "  time  -1 label<TAB>features<TAB>accent"; a line with no label is a
// change of voice quality INSIDE a sound (+sth voiced, +lar creaky, +beh breathy ...), not a new sound
export function parseLabels(text) {
  const out = []; let body = false;
  for (const line of text.split("\n")) {
    if (!body) { if (line.startsWith("#")) body = true; continue; }
    const m = line.match(/^\s*([\d.]+)\s+-?\d+ ?(.*)$/); if (!m) continue;
    const f = m[2].split("\t"); let label = (f[0] ?? "").trim(), feats = (f[1] ?? "").trim();
    if (/^[-+][a-z]/.test(label)) { feats = label; label = ""; }          // "-tie", "+lat": a quality change written where the sound would be
    out.push({ t: +m[1], label, feats, accent: +(f[2] ?? 0) || 0 });
  }
  return out;
}
// a stop is labelled in pieces -- closure "d" (or "_d" utterance-initial), burst "!d", aspiration "dasp" -- one sound here
export function phonesFrom(labels) {
  const ph = []; let order = 9;
  for (let i = 0; i < labels.length; i++) {
    const L = labels[i], t1 = labels[i + 1]?.t ?? L.t;
    if (L.label === ".") break;
    if (!L.label) { if (ph.length) { ph[ph.length - 1].t1 = t1; if (L.feats.includes("+lar")) ph[ph.length - 1].creaky = true; if (L.feats.includes("+beh")) ph[ph.length - 1].breathy = true; } continue; }
    const base = L.label.replace(/^[_!]/, "").replace(/asp$/, ""), part = L.label.endsWith("asp") && L.label.length > 3 ? 2 : L.label.startsWith("!") ? 1 : 0;
    const last = ph[ph.length - 1];
    if (STOPS.includes(base) && base.length === 1 && last && last.sampa === base && part > order) { last.t1 = t1; if (part === 2) last.asp = (last.asp ?? 0) + t1 - L.t; order = part; continue; }
    ph.push({ sampa: base, t0: L.t, t1, accent: L.accent, creaky: L.feats.includes("+lar"), breathy: L.feats.includes("+beh") }); order = STOPS.includes(base) && base.length === 1 ? part : 9;
  }
  return ph;
}
export function ipaFrom(phones, wordStarts = []) {
  let s = "", w = 0;
  for (const p of phones) {
    while (w < wordStarts.length && p.t0 >= wordStarts[w] - 1e-4) { if (s && !s.endsWith(" ")) s += " "; w++; }
    const ipa = SAMPA[p.sampa]; if (ipa === undefined || ipa === "") continue;
    const vowel = /^[aeiouy29EIOUY@6]/.test(p.sampa);
    s += (vowel && p.accent >= 2 ? "ˈ" : "") + ipa + (p.accent >= 2 && TENSE.includes(p.sampa) && p.sampa.length === 1 ? "ː" : "");
  }
  return s.trim();
}
export async function loadTake(corpus, name, fetchBytes, fetchText) {
  const wav = parseWav(await fetchBytes(`${corpus.dir}/wav/${name}.wav`));
  const labels = parseLabels(await fetchText(`${corpus.dir}/lablaut/${name}xx.lablaut`)), phones = phonesFrom(labels);
  const syl = (await fetchText(`${corpus.dir}/silb/${name}.silb`)).split("\n").map((l) => l.split("\t")).filter((c) => c.length > 1 && c[1].trim() !== ".").map((c) => +c[0]);
  const counts = corpus.words[nameParts(name).sentence] ?? [], starts = []; let k = 0;
  if (counts.reduce((a, b) => a + b, 0) === syl.length) for (const c of counts) { starts.push(syl[k]); k += c; }     // (a take that drops a syllable gets no word gaps rather than wrong ones)
  const end = labels.find((l) => l.label === ".")?.t ?? phones[phones.length - 1]?.t1 ?? 0;
  return { name, ...nameParts(name), samples: wav.samples, sr: wav.sr, phones, syllables: syl.length, t0: phones[0]?.t0 ?? 0, t1: end, ipa: ipaFrom(phones, starts), wordsKnown: starts.length > 0 };
}
