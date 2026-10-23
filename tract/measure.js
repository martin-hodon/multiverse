// WHAT THE TUBE RESONATES AT, measured on the tube itself: shut the glottis, knock on it, listen at the lips. The
// formants the lab shows and the inversion fits are therefore exactly the ones the synthesiser will produce -- losses,
// radiation, lip delay and all -- rather than those of a separate, idealised calculation. No imports beyond the tube.
import { Tube } from "./acoustics.js";

export function fft(re, im) {                            // in place, length a power of two
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; } }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = -2 * Math.PI / len, wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) { let cr = 1, ci = 0;
      for (let k = 0; k < len / 2; k++) { const a = i + k, b = a + len / 2, xr = re[b] * cr - im[b] * ci, xi = re[b] * ci + im[b] * cr;
        re[b] = re[a] - xr; im[b] = im[a] - xi; re[a] += xr; im[a] += xi; const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t; } }
  }
}
// the transfer function's magnitude (dB, flow at the glottis -> flow at the lips) and its peaks
export function response(tube, { n = 4096 } = {}) {
  tube.reset(); tube.snap();
  const re = new Float64Array(n), im = new Float64Array(n), shut = { Ps: 0, Ag: 0 };
  let acc = 0;
  for (let i = 0; i < n; i++) { acc += tube.step(shut, i === 0 ? 1000 : 0); re[i] = acc * (.5 + .5 * Math.cos(Math.PI * i / n)); }   // (integrated back to flow; a half-Hann tail)
  fft(re, im);
  const mag = new Float64Array(n / 2); for (let k = 0; k < n / 2; k++) mag[k] = 10 * Math.log10(re[k] * re[k] + im[k] * im[k] + 1e-30);
  tube.reset();
  return { mag, hzPerBin: tube.fs / n };
}
export function formants(tube, { max = 5, from = 150, to = 5500 } = {}) {
  const { mag, hzPerBin } = response(tube), out = [];
  for (let k = Math.max(2, Math.round(from / hzPerBin)); k < Math.min(mag.length - 1, to / hzPerBin) && out.length < max; k++) {
    if (mag[k] > mag[k - 1] && mag[k] >= mag[k + 1]) {
      const a = mag[k - 1], b = mag[k], c = mag[k + 1], off = .5 * (a - c) / (a - 2 * b + c);
      // bandwidth: where the peak has fallen 3dB either side
      let lo = k, hi = k; while (lo > 1 && mag[lo] > b - 3) lo--; while (hi < mag.length - 1 && mag[hi] > b - 3) hi++;
      out.push({ hz: (k + off) * hzPerBin, db: b, bw: (hi - lo) * hzPerBin });
    }
  }
  return out;
}
