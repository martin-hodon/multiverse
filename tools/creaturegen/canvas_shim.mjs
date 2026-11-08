globalThis.Path2D ??= class { constructor() {} addPath() {} moveTo() {} lineTo() {} bezierCurveTo() {} quadraticCurveTo() {} arc() {} arcTo() {} ellipse() {} rect() {} closePath() {} };
// a no-op 2D canvas for node (the people's fabrics draw pattern tiles: patterns.js mkCanvas) -- geometry tests only
globalThis.ImageData ??= class { constructor(a, w, h) { if (typeof a === "number") { h = w; w = a; a = new Uint8ClampedArray(w * h * 4); } this.data = a; this.width = w; this.height = h ?? a.length / 4 / w; } };
if (typeof globalThis.OffscreenCanvas === "undefined") {
  const ctx = (cv) => new Proxy({ canvas: cv }, { get: (t, k) => k in t ? t[k] : k === "getImageData" || k === "createImageData" ? (x, y, w, h) => ({ data: new Uint8ClampedArray(Math.max(1, (w ?? x) * (h ?? y) * 4)), width: w ?? x, height: h ?? y })
    : k === "measureText" ? () => ({ width: 0 }) : k === "createLinearGradient" || k === "createRadialGradient" || k === "createPattern" ? () => ({ addColorStop() {} }) : () => {}, set: (t, k, v) => (t[k] = v, true) });
  globalThis.OffscreenCanvas = class { constructor(w, h) { this.width = w; this.height = h; } getContext() { return this._c ??= ctx(this); } convertToBlob() { return Promise.resolve(new Blob([])); } transferToImageBitmap() { return {}; } };
}
