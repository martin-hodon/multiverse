// VOICE ANALYSIS -- one analyser for a recording of a person and for the synthesiser's output, so that a
// difference between the two is a measurement and not an opinion. No engine imports, no DOM.
//
// Everything is measured in TIME (40ms windows, 10ms hops) and in HERTZ, never in samples or bins, because the
// two sides arrive at different sample rates: studio recordings at 16kHz, the synthesiser at 32kHz. Nothing
// above 7.5kHz is used for the same reason. The absolute values of some of these (CPP above all) depend on
// how they are computed and should not be read against the literature; what matters is that the SAME code
// ran on both.
//
//   const acc = newAnalysis(); addUtterance(acc, samples, sampleRate); ...; const f = finishAnalysis(acc);

export function parseWav(buf) {
  const v = new DataView(buf);
  let p = 12, fmt = null, data = null;
  while (p + 8 <= v.byteLength) {
    const id = String.fromCharCode(v.getUint8(p), v.getUint8(p + 1), v.getUint8(p + 2), v.getUint8(p + 3)), len = v.getUint32(p + 4, true);
    if (id === "fmt ") fmt = { ch: v.getUint16(p + 10, true), sr: v.getUint32(p + 12, true), bits: v.getUint16(p + 22, true) };
    if (id === "data") { data = { at: p + 8, len }; break; }
    p += 8 + len + (len & 1);
  }
  if (!fmt || !data || fmt.bits !== 16) throw new Error("expected 16-bit PCM wav");
  const n = Math.floor(Math.min(data.len, v.byteLength - data.at) / (2 * fmt.ch)), out = new Float32Array(n);
  for (let i = 0; i < n; i++) out[i] = v.getInt16(data.at + i * 2 * fmt.ch, true) / 32768;
  return { samples: out, sr: fmt.sr };
}

export function fft(re, im) {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) { const a = re[i]; re[i] = re[j]; re[j] = a; const b = im[i]; im[i] = im[j]; im[j] = b; }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = -2 * Math.PI / len, wr = Math.cos(ang), wi = Math.sin(ang), h = len >> 1;
    for (let i = 0; i < n; i += len) {
      let cr = 1, ci = 0;
      for (let k = 0; k < h; k++) {
        const a = i + k, b = a + h, vr = re[b] * cr - im[b] * ci, vi = re[b] * ci + im[b] * cr;
        re[b] = re[a] - vr; im[b] = im[a] - vi; re[a] += vr; im[a] += vi;
        const nr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = nr;
      }
    }
  }
}

// the bands the long-term spectrum is read in, Hz
export const BANDS = [[50, 250], [250, 500], [500, 1000], [1000, 2000], [2000, 3000], [3000, 4000], [4000, 5500], [5500, 7500]];
const FLUX_EDGES = Array.from({ length: 17 }, (_, i) => 200 * Math.pow(5000 / 200, i / 16));   // 16 log bands, 200Hz-5kHz

// PITCH. Normalised autocorrelation on the signal decimated to ~8kHz, and the SHORTEST lag within 10% of the
// best -- plain autocorrelation lands an octave down on a creaky or breathy voice, and then "H1" is measured
// on the wrong harmonic and every number after it is fiction. Returns [f0, how periodic 0-1].
function pitch(w, sr, lo = 65, hi = 420) {
  const q = Math.max(1, Math.round(sr / 8000)), d = new Float64Array(Math.floor(w.length / q));
  for (let i = 0; i < d.length; i++) { let s = 0; for (let k = 0; k < q; k++) s += w[i * q + k]; d[i] = s / q; }
  const r8 = sr / q, minL = Math.max(2, Math.floor(r8 / hi)), maxL = Math.min(Math.floor(r8 / lo), d.length - 30);
  const r = new Float64Array(maxL + 1);
  let best = 0;
  for (let lag = minL; lag <= maxL; lag++) {
    let num = 0, e1 = 0, e2 = 0;
    for (let i = 0; i + lag < d.length; i++) { num += d[i] * d[i + lag]; e1 += d[i] * d[i]; e2 += d[i + lag] * d[i + lag]; }
    r[lag] = num / Math.sqrt(e1 * e2 + 1e-12);
    if (r[lag] > best) best = r[lag];
  }
  if (best < .45) return [0, best];
  for (let lag = minL + 1; lag < maxL; lag++) {
    if (r[lag] >= best * .9 && r[lag] >= r[lag - 1] && r[lag] >= r[lag + 1]) {
      const a = r[lag - 1], b = r[lag], c = r[lag + 1], den = a - 2 * b + c, off = den ? .5 * (a - c) / den : 0;   // parabolic peak
      return [r8 / (lag + off), best];
    }
  }
  return [0, best];
}

export function newAnalysis() {
  return { ltasV: null, ltasAll: null, nV: 0, nAll: 0, hz: 0, f0: [], h1h2: [], h1a3: [], cpp: [], level: [], flux: [],
           perturb: [], speech: 0, voiced: 0, total: 0, peaks: 0 };
}

export function addUtterance(A, x, sr) {
  const W = Math.round(sr * .04), hop = Math.round(sr * .01);
  let N = 1024; while (N < 2 * W) N <<= 1;
  const hzPerBin = sr / N, half = N / 2, bin = (hz) => Math.min(half - 1, Math.round(hz / hzPerBin));
  // the long-term spectra are kept on a fixed 10Hz grid so that 16kHz and 32kHz material land in the same bins
  if (!A.ltasV) { A.ltasV = new Float64Array(760); A.ltasAll = new Float64Array(760); }
  const re = new Float64Array(N), im = new Float64Array(N), mag = new Float64Array(half), hann = new Float64Array(W);
  for (let i = 0; i < W; i++) hann[i] = .5 - .5 * Math.cos(2 * Math.PI * i / (W - 1));
  // levels at the 10ms hop, for the dynamics and for where the speech is
  const nF = Math.max(0, Math.floor((x.length - W) / hop)), lev = new Float64Array(nF);
  let top = -200;
  for (let f = 0; f < nF; f++) { let e = 0; for (let i = 0; i < W; i++) { const v = x[f * hop + i]; e += v * v; } lev[f] = 10 * Math.log10(e / W + 1e-12); top = Math.max(top, lev[f]); }
  const floor = top - 35;
  // TWO PASSES. Tracked over the whole 65-420Hz range, about one frame in twenty lands an octave out -- at fast
  // transitions, mostly -- and a handful of those is enough to double a voice's apparent pitch span. So the first
  // pass only finds where this speaker's pitch lives, and the second tracks each frame within 0.6-1.7x of that.
  const rough = [];
  for (let f = 0; f < nF; f += 4) if (lev[f] >= floor) { const [p] = pitch(x.subarray(f * hop, f * hop + W), sr); if (p) rough.push(p); }
  rough.sort((p, q) => p - q);
  const med = rough.length ? rough[rough.length >> 1] : 0, pLo = med ? med * .6 : 65, pHi = med ? med * 1.7 : 420;
  let prevBands = null, prevF0 = 0, prevAt = -9;
  for (let f = 0; f < nF; f++) {
    A.total++;
    if (lev[f] < floor) { prevBands = null; continue; }
    A.speech++; A.level.push(lev[f] - top);
    if (f > 1 && f < nF - 2 && lev[f] > lev[f - 1] && lev[f] >= lev[f + 1] && lev[f] > lev[f - 2] + 1.5 && lev[f] > top - 22) A.peaks++;
    if (f & 1) continue;                                   // spectra every 20ms: half the work, the same answer
    const seg = x.subarray(f * hop, f * hop + W);
    re.fill(0); im.fill(0);
    for (let i = 0; i < W; i++) re[i] = seg[i] * hann[i];
    fft(re, im);
    for (let k = 0; k < half; k++) mag[k] = re[k] * re[k] + im[k] * im[k] + 1e-20;   // power
    const [f0, per] = pitch(seg, sr, pLo, pHi);
    const grid = (dst) => { for (let g = 0; g < 760; g++) { const k = (g * 10 + 5) / hzPerBin, k0 = Math.floor(k), t = k - k0; if (k0 + 1 < half) dst[g] += mag[k0] * (1 - t) + mag[k0 + 1] * t; } };
    grid(A.ltasAll); A.nAll++;
    if (!f0) { prevBands = null; continue; }
    A.voiced++; grid(A.ltasV); A.nV++; A.f0.push(f0);
    if (prevF0 && f - prevAt === 2) A.perturb.push(Math.abs(f0 - prevF0) / prevF0 * 100);
    prevF0 = f0; prevAt = f;
    // harmonics: the strongest bin within 12% of where each should be
    const peak = (hz) => { let m = 0; for (let k = Math.max(1, bin(hz * .88)); k <= bin(hz * 1.12); k++) m = Math.max(m, mag[k]); return 10 * Math.log10(m); };
    const h1 = peak(f0), h2 = peak(2 * f0);
    let a3 = -300; for (let k = bin(2000); k <= bin(3500); k++) a3 = Math.max(a3, 10 * Math.log10(mag[k]));
    A.h1h2.push(h1 - h2); A.h1a3.push(h1 - a3);
    // how fast the spectrum is moving: the mean change across 16 log bands since the last voiced window (20ms)
    const bands = new Float64Array(16);
    for (let b = 0; b < 16; b++) { let e = 0; for (let k = bin(FLUX_EDGES[b]); k <= bin(FLUX_EDGES[b + 1]); k++) e += mag[k]; bands[b] = 10 * Math.log10(e + 1e-20); }
    if (prevBands) { let d = 0; for (let b = 0; b < 16; b++) d += Math.abs(bands[b] - prevBands[b]); A.flux.push(d / 16); }
    prevBands = bands;
    // CEPSTRAL PEAK PROMINENCE: how far the pitch period's peak stands above the trend of the cepstrum. It is
    // the most robust single number for "how periodic, how breathy". It MUST be taken over the same band on
    // both sides: over the whole spectrum, a 32kHz signal carries an empty octave above 8kHz that a 16kHz
    // recording does not have, which dilutes the peak and reads as a breathier voice whatever the voice is
    // doing. So the log spectrum is resampled onto 1024 points across 0-7.5kHz and mirrored to 2048 -- the
    // cepstrum then has quefrency bins of 1/15000s for any input.
    const CG = 1024, CL = 2048, cre = A.cre ?? (A.cre = new Float64Array(CL)), cim = A.cim ?? (A.cim = new Float64Array(CL));
    for (let g = 0; g < CG; g++) {
      const k = g * (7500 / CG) / hzPerBin, k0 = Math.floor(k), t = k - k0;
      cre[g] = 10 * Math.log10(mag[k0] * (1 - t) + mag[Math.min(half - 1, k0 + 1)] * t);
    }
    for (let g = CG; g < CL; g++) cre[g] = cre[CL - 1 - g];
    cim.fill(0);
    fft(cre, cim);
    const cep = (k) => 10 * Math.log10(cre[k] * cre[k] + cim[k] * cim[k] + 1e-12), qsr = 15000;
    const kLo = Math.round(qsr / 420), kHi = Math.round(qsr / 65);
    let pk = -300, pkAt = kLo;
    for (let k = kLo; k <= kHi; k++) { const c = cep(k); if (c > pk) { pk = c; pkAt = k; } }
    let sx = 0, sy = 0, sxx = 0, sxy = 0, m = 0;          // the regression line from 1ms out
    for (let k = Math.round(qsr * .001); k <= kHi; k++) { const c = cep(k); sx += k; sy += c; sxx += k * k; sxy += k * c; m++; }
    const slope = (m * sxy - sx * sy) / (m * sxx - sx * sx), icpt = (sy - slope * sx) / m;
    A.cpp.push(pk - (icpt + slope * pkAt));
  }
  A.hz += x.length / sr;
}

const mean = (a) => a.reduce((p, q) => p + q, 0) / Math.max(1, a.length);
const sdev = (a) => { const m = mean(a); return Math.sqrt(mean(a.map((v) => (v - m) ** 2))); };
const pct = (a, p) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.min(s.length - 1, Math.floor(p * s.length))] : 0; };

export function finishAnalysis(A) {
  const st = A.f0.map((f) => 12 * Math.log2(f)), band = (src, n, lo, hi) => { let e = 0; for (let g = Math.floor(lo / 10); g < Math.floor(hi / 10); g++) e += src[g]; return e / Math.max(1, n); };
  const tot = band(A.ltasV, A.nV, 50, 7500), totAll = band(A.ltasAll, A.nAll, 50, 7500);
  return {
    f0: pct(A.f0, .5), f0sd: sdev(st), f0span: pct(st, .95) - pct(st, .05), f0pct: [.02, .05, .25, .75, .95, .98].map((p) => Math.round(pct(A.f0, p))),
    h1h2: mean(A.h1h2), h1a3: mean(A.h1a3), cpp: mean(A.cpp), cppSd: sdev(A.cpp),
    ltas: BANDS.map(([lo, hi]) => 10 * Math.log10(band(A.ltasV, A.nV, lo, hi) / tot + 1e-12)),
    hfAll: 10 * Math.log10(band(A.ltasAll, A.nAll, 4000, 7500) / totAll + 1e-12),   // with the fricatives in
    levelSd: sdev(A.level), flux: mean(A.flux), perturb: pct(A.perturb, .5),
    voicedShare: A.voiced * 2 / Math.max(1, A.speech), rate: A.peaks / Math.max(.1, A.speech * .01), seconds: A.speech * .01,
  };
}
