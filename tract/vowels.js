// WHAT EACH VOWEL SHOULD SOUND LIKE: its first three formants for the reference adult male tract (Hz). These are the
// targets the inversion (inversion.js) fits postures to; the postures it found are in postures.json, and are what the
// synthesiser actually uses -- edit either, and re-run the inversion from the lab if you change these.
export const VOWEL_TARGETS = {
  i: [280, 2250, 2900], "ɪ": [400, 1900, 2550], e: [400, 2100, 2650], "ɛ": [550, 1800, 2500], "æ": [690, 1660, 2450], a: [750, 1300, 2500], "ɑ": [730, 1090, 2440],
  "ɔ": [570, 840, 2410], o: [450, 800, 2400], "ʊ": [440, 1020, 2240], u: [310, 870, 2250], "ə": [500, 1400, 2500], "ʌ": [640, 1190, 2390], "ɜ": [490, 1350, 1700], "ɐ": [600, 1300, 2500],
  y: [270, 1900, 2200], "ʏ": [350, 1700, 2200], "ø": [400, 1550, 2200], "œ": [500, 1450, 2300], "ɨ": [350, 1500, 2400], "ɤ": [500, 1150, 2500],
};
