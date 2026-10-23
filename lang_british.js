// BRITISH ENGLISH FROM THE AMERICAN DICTIONARY. The concept files in lang/ hold ONE English column, General American
// (lang/IPA-GUIDE.md). The British list (lang/words/en-GB.txt, lang/function-words/en-GB.txt) is DERIVED from it by the
// regular correspondences between the two accents, plus a table of the words that simply differ. It is compiled with the other
// word lists (rule_tester.html?gen=1); to correct a British pronunciation, add the word to WORDS below and regenerate.
//
// The target is a modern southern British accent in the dictionary's own conventions (ɹ for r, ɛ for DRESS, æ for TRAP):
//   LOT     ɑ -> ɒ (not, dog, want)              CLOTH   ɔː -> ɒ where spelled with o (off, long, cost)
//   GOAT    oʊ -> əʊ                             BATH    æ -> ɑː in the BATH words (ask, glass, dance, half ...)
//   r       is said only before a vowel: car kɑː, letter ˈlɛtə, near nɪə, square skwɛə, cure kjʊə, fire ˈfaɪə, nurse nɜːs;
//           hurry ˈhʌɹi, very ˈvɛɹi, carry ˈkæɹi, parent ˈpɛəɹənt, serious ˈsɪəɹiəs, orange ˈɒɹɪndʒ
//   yod     t d n + uː spelled u / ew / eu keep their j: new njuː, tune tjuːn, duty ˈdjuːti, student ˈstjuːdənt
//   -ile    fragile ˈfɹædʒaɪl        -ary / -ory / -ery, unstressed: secretary ˈsɛkɹətɹi, category ˈkætəɡɹi
// No DOM, no imports.

const DIPH = ["eɪ", "oʊ", "aɪ", "aʊ", "ɔɪ"], VOWELS = "iɪeɛæaɑɒɔoʊuəʌɜɐ";
// the vowel nuclei of a pronunciation: [{ at, end, text }]
function nuclei(ipa) { const out = []; for (let i = 0; i < ipa.length;) { let j; if (DIPH.includes(ipa.slice(i, i + 2))) j = i + 2; else if (VOWELS.includes(ipa[i])) j = i + 1; else { i++; continue; } while (j < ipa.length && "ː̃".includes(ipa[j])) j++; out.push({ at: i, end: j, text: ipa.slice(i, j) }); i = j; } return out; }
// the vowel-letter groups of a spelling (a silent final e dropped): [{ at, text }]
function groups(word) { const w = word.toLowerCase(), gs = []; for (const m of w.matchAll(/[aeiouy]+/g)) { let g = m[0], s = m.index; if (s === 0 && g[0] === "y") { g = g.slice(1); s++; if (!g) continue; } gs.push({ at: s, text: g }); }
  const last = gs[gs.length - 1], cons = (c) => c && !"aeiouy".includes(c);
  if (gs.length > 1 && last.text === "e" && last.at === w.length - 1 && cons(w[w.length - 2])) gs.pop();
  else if (gs.length > 1 && last.text === "e" && /e[sd]$/.test(w) && last.at === w.length - 2 && cons(w[w.length - 3]) && !"sxztd".includes(w[w.length - 3])) gs.pop();
  return gs; }
// the spelling of the k-th nucleus, when spelling and sound have the same number of vowels (else null: no guessing)
const spelled = (word, ipa, k) => { const gs = groups(word); return gs.length === nuclei(ipa).length ? gs[k] : null; };

// the BATH words (their stems: compounds and inflections match by containing them at a word boundary of the spelling)
const BATH = ("after ask aunt answer bath basket behalf branch brass calf can't cast castle chance class command craft dance demand disaster draft draught example " +
  "fast fasten france ghastly giraffe glance glass graph grant grasp grass half last laugh mask mast master nasty pass past pasture path plant plaster rather raft " +
  "sample shaft slant staff task vast advance advantage banana broadcast forecast telegraph photograph paragraph autograph enchant chant plaza lather").split(" ");
const NOT_BATH = /^(passage|passenger|passion|passive|classic|classify|classical|massive|mass|gas|plastic|fantastic|drastic|elastic|bass|lass|asp|aspect|aspirin|pasta|pastel|castor|mascot|masculine|tassel|hassle|graphic|grand|grandmother|grandfather)/;
const ORANGE = /^(orange|forest|horr|foreign|origin|moral|coral|florist|historic|authorit|majorit|minorit|priorit|categoric|correspond|coronat|corridor|correlat|quarrel|warrant|warrior|porridge|torrent|florid|tolerat|laborator|borrow|sorrow|tomorrow|sorry|oracle|orifice|orator)/;
// the words that simply differ (British pronunciation in full, the dictionary's conventions). Inflected forms are not derived from these.
export const WORDS = {
  schedule: "ˈʃɛdjuːl", tomato: "təˈmɑːtəʊ", vitamin: "ˈvɪtəmɪn", privacy: "ˈpɹɪvəsi", leisure: "ˈlɛʒə", either: "ˈaɪðə", neither: "ˈnaɪðə", herb: "hɜːb",
  garage: "ˈɡæɹɑːʒ", ballet: "ˈbæleɪ", buffet: "ˈbʊfeɪ", cafe: "ˈkæfeɪ", "café": "ˈkæfeɪ", adult: "ˈædʌlt", advertisement: "ədˈvɜːtɪsmənt", laboratory: "ləˈbɒɹətɹi",
  lieutenant: "lɛfˈtɛnənt", yogurt: "ˈjɒɡət", yoghurt: "ˈjɒɡət", zebra: "ˈzɛbɹə", clerk: "klɑːk", vase: "vɑːz", route: "ɹuːt", data: "ˈdeɪtə", progress: "ˈpɹəʊɡɹɛs",
  process: "ˈpɹəʊsɛs", been: "biːn", figure: "ˈfɪɡə", thorough: "ˈθʌɹə", borough: "ˈbʌɹə", squirrel: "ˈskwɪɹəl", syrup: "ˈsɪɹəp", stirrup: "ˈstɪɹəp", hurricane: "ˈhʌɹɪkən",
  moustache: "məˈstɑːʃ", mustache: "məˈstɑːʃ", massage: "ˈmæsɑːʒ", pasta: "ˈpæstə", taco: "ˈtækəʊ", mafia: "ˈmæfiə", what: "wɒt", was: "wɒz", from: "fɹɒm", because: "bɪˈkɒz",
  everybody: "ˈɛvɹibɒdi", anybody: "ˈɛnibɒdi", nobody: "ˈnəʊbədi", somebody: "ˈsʌmbədi", asthma: "ˈæsmə", version: "ˈvɜːʃən", erase: "ɪˈɹeɪz", lever: "ˈliːvə", medicine: "ˈmɛdsən",
  migraine: "ˈmiːɡɹeɪn", zenith: "ˈzɛnɪθ", dynasty: "ˈdɪnəsti", address: "əˈdɹɛs", cigarette: "sɪɡəˈɹɛt", magazine: "mæɡəˈziːn", weekend: "wiːkˈɛnd", princess: "pɹɪnˈsɛs",
  controversy: "ˈkɒntɹəvɜːsi", patriot: "ˈpætɹiət", collage: "ˈkɒlɑːʒ", croissant: "ˈkwæsɒ̃", genre: "ˈʒɒnɹə", fiance: "fiˈɒnseɪ", "fiancé": "fiˈɒnseɪ", "fiancée": "fiˈɒnseɪ",
  restaurant: "ˈɹɛstɹɒnt", shone: "ʃɒn", ate: "ɛt", niche: "niːʃ", apricot: "ˈeɪpɹɪkɒt", oregano: "ɒɹɪˈɡɑːnəʊ", basil: "ˈbæzəl", compost: "ˈkɒmpɒst", yoga: "ˈjəʊɡə",
  docile: "ˈdəʊsaɪl", nougat: "ˈnuːɡɑː", premier: "ˈpɹɛmiə", renaissance: "ɹɪˈneɪsəns", status: "ˈsteɪtəs", twenty: "ˈtwɛnti", z: "zɛd", water: "ˈwɔːtə", iron: "ˈaɪən",
  worry: "ˈwʌɹi", courage: "ˈkʌɹɪdʒ", nourish: "ˈnʌɹɪʃ", current: "ˈkʌɹənt", currency: "ˈkʌɹənsi", hurry: "ˈhʌɹi", curry: "ˈkʌɹi", turret: "ˈtʌɹɪt", furrow: "ˈfʌɹəʊ", burrow: "ˈbʌɹəʊ",
  for: "fɔː", or: "ɔː", are: "ɑː", were: "wɜː", her: "hɜː", your: "jɔː", our: "ˈaʊə", their: "ðɛə", there: "ðɛə", where: "wɛə", here: "hɪə", sure: "ʃɔː", poor: "pɔː",
};

const isVowelAt = (s, i) => { while (s[i] === "ˈ" || s[i] === "ˌ" || s[i] === ".") i++; return i < s.length && VOWELS.includes(s[i]); };

export function toBritish(word, ipa) {
  const w = word.toLowerCase().normalize("NFC"); if (WORDS[w]) return WORDS[w];
  let p = ipa;
  // ---- vowels that go by the spelling: CLOTH (ɔː spelled o), yod (t d n + uː spelled u / ew / eu). Worked out before anything moves.
  { const nu = nuclei(p); let out = "", from = 0;
    nu.forEach((v, k) => { const g = spelled(w, p, k); let text = v.text;
      if (v.text === "ɔː" && p[v.end] !== "ɹ" && g && /^o(?![uaw])/.test(g.text) && !/^o(r|l[dtk]|ll|st$)/.test(w.slice(g.at))) text = "ɒ";      // off, long, cost, dog -- not old, toll, most
      if (v.text === "uː" && "tdn".includes(p[v.at - 1] ?? "") && g && /^(u|ew|eu|ue)/.test(w.slice(g.at))) text = "j" + text;
      out += p.slice(from, v.at) + text; from = v.end; });
    p = out + p.slice(from); }
  // ---- BATH
  if (!NOT_BATH.test(w) && BATH.some((b) => new RegExp(`(^|[^a-z])${b.replace("'", "['’]?")}`).test(w) || (b.length >= 4 && new RegExp(`${b}(s|ed|ing)?$`).test(w)))) { const i = p.search(/æ(?=[fsθnm]|$)/); const j = i >= 0 ? i : p.indexOf("æ"); if (j >= 0) p = p.slice(0, j) + "ɑː" + p.slice(j + 1); }
  // ---- unstressed -ary / -ory / -ery / -erry and -ile
  // (the ending is unstressed when the stress lies at least two syllables before the last: SECretary, CATegory, LIbrary, CEremony -- not caNAry, STOry)
  if (/(ary|ory|ery|erry|ony)$/.test(w)) { const tail = p.match(/(ɛɹi|ɔːɹi|oʊni)$/);
    if (tail && nuclei(p.slice(p.lastIndexOf("ˈ") + 1)).length >= 3) { const head = p.slice(0, -tail[0].length), afterCons = !VOWELS.includes(head.slice(-1)) && head.slice(-1) !== "ɹ" && head.slice(-1) !== "ː";
      p = head + (tail[0] === "oʊni" ? "əni" : afterCons && !/erry$/.test(w) ? "ɹi" : "əɹi"); } }
  if (/ile$/.test(w) && /əl$/.test(p)) p = p.slice(0, -2) + "aɪl";
  // ---- LOT, GOAT
  p = p.replace(/ɑ(?!ː|̃)/g, "ɒ").replace(/oʊ/g, "əʊ");
  if (ORANGE.test(w)) p = p.replace(/ɔːɹ(?=ˈ?[iɪeɛæaɑɒɔoʊuəʌɜ])/, "ɒɹ");
  // ---- r: what it does to the vowel before it, then gone unless a vowel follows
  const V = "(?=[ˈˌ]?[" + VOWELS + "])", notV = "(?![ˈˌ]?[" + VOWELS + "])";
  const SQUARE = /ari(a|an|um|ous|ety)|ar(y|ea)$|^(parent|var[yi]|mary|scar|war[ye]|rar|car(ing|e)|shar|dar[ei]|bar(e|ing)|star(e|ing)|squar|prepar|compar(e|ing)|declar|aware|hair|fair|dair|air|chair|pair|stair|wear|bear|pear|tear|swear)|aer/;
  p = p.replace(new RegExp("ɜːɹ" + V, "g"), /urr|orr|our|(^|[^e])or[aeiouy]/.test(w) ? "ʌɹ" : "ɜːɹ")                                   // hurry, worry, courage -- not furry (rare)
    .replace(new RegExp("ɛɹ" + V, "g"), /arr/.test(w) ? "æɹ" : SQUARE.test(w) ? "ɛəɹ" : /ar[aeiouy]/.test(w) && !/er[aeiouy]|err/.test(w) ? "æɹ" : "ɛɹ")   // carry; parent, various; character; very
    .replace(new RegExp("ɪɹ" + V, "g"), /irr?[aeiouy]|yr/.test(w) ? "ɪɹ" : "ɪəɹ")                                                     // spirit, mirror, lyric; serious, period, hero
    .replace(new RegExp("ʊɹ" + V, "g"), "ʊəɹ")
    .replace(new RegExp("aɪɹ" + notV, "g"), "aɪə").replace(new RegExp("aʊɹ" + notV, "g"), "aʊə")
    .replace(new RegExp("ɛɹ" + notV, "g"), "ɛə").replace(new RegExp("ɪɹ" + notV, "g"), "ɪə").replace(new RegExp("ʊɹ" + notV, "g"), "ʊə");
  let out = ""; for (let i = 0; i < p.length; i++) { if (p[i] === "ɹ" && !isVowelAt(p, i + 1)) continue; out += p[i]; }
  return out.replace(/əə/g, "ə");
}
// a British word that ends in a written r says it again before a vowel ("far away", "here is"): the linking r
export const linksR = (written, ipa) => /(r|re)$/i.test(written) && /(ə|ɑː|ɔː|ɜː)$/.test(ipa);
