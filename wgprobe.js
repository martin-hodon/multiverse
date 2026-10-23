// A HEADLESS EYE FOR WEBGPU.
// Chromium runs WebGPU without a screen, but nothing about the picture comes back the usual ways: there is no
// frame loop (requestAnimationFrame never fires), the canvas is never presented (so --screenshot and drawImage
// both return an empty image), and three's own readRenderTargetPixelsAsync waits for a device tick that never
// comes. What does work is plain WebGPU: render into a render target, copy its texture into a buffer and map
// it. This module does that and prints the frame as an ASCII thumbnail plus a colour tally -- enough to tell
// "nine parts in the right places" from "one black card", which is the whole question a shader change raises.
const RAMP = " .:-=+*#%@";

/**
 * The renderer to use when the page is being checked headless. Chromium runs WebGPU without a screen, but it
 * cannot make the canvas swap-chain, and merely ASKING for one drops the whole WebGPU instance -- after which
 * every buffer read fails with "Instance dropped". So the headless renderer gets a canvas whose webgpu context
 * is a stub: nothing is ever presented, and probe() renders into a render target instead.
 * Returns an UNINITIALISED renderer -- await renderer.init() yourself, and call setSize AFTER that.
 */
export async function headlessRenderer(params = {}) {
  const THREE = await import("three");
  const cv = document.createElement("canvas");
  let renderer = null, fake = null;
  // ...and when something does render to "the screen", it gets a throwaway texture of the right size and
  // format. Nothing is ever presented; the picture that matters comes back through probe().
  const context = {
    configure() {}, unconfigure() {},
    getCurrentTexture() {
      const device = renderer?.backend?.device;
      if (!device) throw new Error("headless: no device yet");
      const w = Math.max(1, cv.width), h = Math.max(1, cv.height);
      if (!fake || fake.width !== w || fake.height !== h) {
        fake?.destroy?.();
        fake = device.createTexture({
          size: [w, h], format: navigator.gpu.getPreferredCanvasFormat(),
          usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC | GPUTextureUsage.TEXTURE_BINDING,
        });
      }
      return fake;
    },
  };
  cv.getContext = () => context;
  renderer = new THREE.WebGPURenderer({ ...params, canvas: cv, antialias: false });
  return renderer;
}

/** is this a real WebGPU backend, or did three quietly fall back to WebGL? (headless without the right flags does) */
export const backendName = (renderer) => renderer.backend?.isWebGPUBackend ? "WebGPU" : "WebGL (fallback!)";

export async function probe(renderer, scene, camera, opts = {}) {
  try { return await probeInner(renderer, scene, camera, opts); }
  catch (e) { try { await fetch("/report", { method: "POST", body: "PROBE ERR: " + (e?.message ?? e) }); } catch {} throw e; }
}

async function probeInner(renderer, scene, camera, { w = 64, h = 32, id = "probe", report = true, chars = null } = {}) {
  const THREE = await import("three");
  const W = w * 4, H = h * 8;
  const rt = new THREE.RenderTarget(W, H, { depthBuffer: true });
  const prev = renderer.getRenderTarget();
  renderer.setRenderTarget(rt);
  await renderer.renderAsync(scene, camera);
  renderer.setRenderTarget(prev);

  const device = renderer.backend.device;
  const gtex = renderer.backend.get(rt.texture).texture;
  const bpr = Math.ceil(W * 4 / 256) * 256;                       // WebGPU wants rows aligned to 256 bytes
  const buf = device.createBuffer({ size: bpr * H, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
  const enc = device.createCommandEncoder();
  enc.copyTextureToBuffer({ texture: gtex }, { buffer: buf, bytesPerRow: bpr }, { width: W, height: H });
  device.queue.submit([enc.finish()]);
  await buf.mapAsync(GPUMapMode.READ);
  const raw = new Uint8Array(buf.getMappedRange()).slice();
  buf.unmap();
  const bgra = (gtex.format || "").startsWith("bgra");
  const at = (x, y) => {
    const i = y * bpr + x * 4;
    return bgra ? [raw[i + 2], raw[i + 1], raw[i]] : [raw[i], raw[i + 1], raw[i + 2]];
  };

  const cellW = W / w | 0, cellH = H / h | 0;
  let art = "";
  for (let cy = 0; cy < h; cy++) {
    for (let cx = 0; cx < w; cx++) {
      let r = 0, g = 0, b = 0, n = 0;
      for (let y = 0; y < cellH; y += 2) for (let x = 0; x < cellW; x += 2) {
        const c = at(cx * cellW + x, cy * cellH + y); r += c[0]; g += c[1]; b += c[2]; n++;
      }
      if (chars) {
        // classify the cell by the nearest named colour: this is how "which part won this pixel" is read back,
        // and so how per-pixel depth is checked without a screen
        let best = ".", bd = Infinity;
        for (const c of chars) {
          const d = (r / n - c.rgb[0]) ** 2 + (g / n - c.rgb[1]) ** 2 + (b / n - c.rgb[2]) ** 2;
          if (d < bd) { bd = d; best = c.ch; }
        }
        art += best;
      } else {
        const lum = (r * .3 + g * .6 + b * .1) / n / 255;
        art += RAMP[Math.min(9, Math.max(0, Math.round(lum * 9)))];
      }
    }
    art += "\n";
  }
  // the colour tally, quantised so antialiasing does not shatter it into hundreds of near-identical entries
  const tally = new Map();
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const c = at(x, y); const k = `${c[0] >> 4},${c[1] >> 4},${c[2] >> 4}`;
    tally.set(k, (tally.get(k) || 0) + 1);
  }
  const top = [...tally].sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([k, c]) => `${k.split(",").map(v => (+v) * 16 + 8).join(",")} ${(100 * c / (W * H)).toFixed(1)}%`).join(" | ");

  const text = art + "colours: " + top;
  if (report) { try { await fetch("/report", { method: "POST", body: text }); } catch {} }
  const pre = document.createElement("pre");
  pre.id = id;
  pre.style.cssText = "position:fixed;left:8px;bottom:8px;background:#fff;color:#000;font:9px/9px monospace;padding:6px;z-index:9";
  pre.textContent = text;
  document.body.appendChild(pre);
  return { art, top };
}

/** the generated shader, posted back: the only way to see what the node graph actually produced */
export async function dumpShader(renderer, scene, camera, mesh, { report = true } = {}) {
  const src = await renderer.debug.getShaderAsync(scene, camera, mesh);
  const text = "=== VERTEX ===\n" + src.vertexShader + "\n=== FRAGMENT ===\n" + src.fragmentShader;
  if (report) { try { await fetch("/report", { method: "POST", body: text }); } catch {} }
  return text;
}

/**
 * The raw frame, posted as hex -- for comparing one backend against another rather than eyeballing ASCII.
 * Same render-target route as probe(), because it is the only read-back that works headless.
 */
export async function pixels(renderer, scene, camera, { w = 64, h = 64, report = true, tag = "px" } = {}) {
  const THREE = await import("three");
  // A STENCIL BUFFER TOO. The canvas has one (the engines' conservative-depth emulation needs it), and three
  // only builds a material's stencil state when the target it is drawing into has stencil -- so a target
  // without one silently ignores every stencil test, and a check run here would prove nothing about the page.
  const rt = new THREE.RenderTarget(w, h, { depthBuffer: true, stencilBuffer: true });
  const prev = renderer.getRenderTarget();
  renderer.setRenderTarget(rt);
  await renderer.renderAsync(scene, camera);
  renderer.setRenderTarget(prev);
  const device = renderer.backend.device;
  const gtex = renderer.backend.get(rt.texture).texture;
  const bpr = Math.ceil(w * 4 / 256) * 256;
  const buf = device.createBuffer({ size: bpr * h, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
  const enc = device.createCommandEncoder();
  enc.copyTextureToBuffer({ texture: gtex }, { buffer: buf, bytesPerRow: bpr }, { width: w, height: h });
  device.queue.submit([enc.finish()]);
  await buf.mapAsync(GPUMapMode.READ);
  const raw = new Uint8Array(buf.getMappedRange()).slice();
  buf.unmap();
  const bgra = (gtex.format || "").startsWith("bgra");
  const out = new Uint8Array(w * h * 3);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * bpr + x * 4, o = (y * w + x) * 3;
    out[o] = bgra ? raw[i + 2] : raw[i]; out[o + 1] = raw[i + 1]; out[o + 2] = bgra ? raw[i] : raw[i + 2];
  }
  const hex = [...out].map((v) => v.toString(16).padStart(2, "0")).join("");
  if (report) { try { await fetch("/report", { method: "POST", body: tag + " " + w + " " + h + " " + hex }); } catch {} }
  return out;
}
