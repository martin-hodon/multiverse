// the head section, the area function and a spectrum, drawn on a 2D canvas (the lab and the headless checks share it)
export function drawSagittal(ctx, sg, { x = 0, y = 0, w = 420, h = 420, ink = "#222", soft = "#c9b8a6", air = "#e8f1f7" } = {}) {
  const k = Math.min(w / 11, h / 10), X = (p) => x + (p[0] + 1.6) * k, Y = (p) => y + h - (p[1] + 1.2) * k;
  ctx.save(); ctx.lineJoin = "round"; ctx.lineCap = "round";
  // the airway: the quads between successive measuring lines
  ctx.fillStyle = air; for (let i = 0; i + 1 < sg.cuts.length; i++) { const a = sg.cuts[i], b = sg.cuts[i + 1]; ctx.beginPath(); ctx.moveTo(X(a.wall), Y(a.wall)); ctx.lineTo(X(b.wall), Y(b.wall)); ctx.lineTo(X(b.tongue), Y(b.tongue)); ctx.lineTo(X(a.tongue), Y(a.tongue)); ctx.closePath(); ctx.fill(); }
  // the tongue
  ctx.fillStyle = soft; ctx.beginPath(); ctx.moveTo(X(sg.hy), Y(sg.hy)); ctx.lineTo(X(sg.tRoot), Y(sg.tRoot));
  const rx = sg.rx ?? sg.r, ry = sg.ry ?? sg.r;      // (the body is the reference head's circle, stretched with the head)
  const a0 = Math.atan2((sg.tRoot[1] - sg.C[1]) / ry, (sg.tRoot[0] - sg.C[0]) / rx), a1 = Math.atan2((sg.tBlade[1] - sg.C[1]) / ry, (sg.tBlade[0] - sg.C[0]) / rx);
  { let t0 = a0, t1 = a1; while (t1 > t0) t1 -= 2 * Math.PI;                 // from the root tangent, over the top (clockwise as drawn), to the blade tangent
    for (let q = 0; q <= 24; q++) { const t = t0 + (t1 - t0) * q / 24; ctx.lineTo(X([sg.C[0] + rx * Math.cos(t), sg.C[1] + ry * Math.sin(t)]), Y([sg.C[0] + rx * Math.cos(t), sg.C[1] + ry * Math.sin(t)])); } }
  ctx.lineTo(X(sg.tip), Y(sg.tip)); for (const p of sg.floor) ctx.lineTo(X(p), Y(p)); ctx.lineTo(X([sg.teeth[0], sg.hy[1]]), Y([sg.teeth[0], sg.hy[1]])); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = ink; ctx.lineWidth = 2; ctx.beginPath(); sg.wall.forEach((p, i) => i ? ctx.lineTo(X(p), Y(p)) : ctx.moveTo(X(p), Y(p))); ctx.stroke();           // the fixed wall
  ctx.lineWidth = 1; ctx.strokeStyle = "rgba(0,0,0,.18)"; for (const c of sg.cuts) { ctx.beginPath(); ctx.moveTo(X(c.wall), Y(c.wall)); ctx.lineTo(X(c.tongue), Y(c.tongue)); ctx.stroke(); }
  // teeth and lips
  ctx.fillStyle = "#fff"; ctx.strokeStyle = ink; const tooth = (p, up) => { ctx.beginPath(); ctx.moveTo(X(p), Y(p)); ctx.lineTo(X([p[0] - .22, p[1] + up * .75]), Y([p[0] - .22, p[1] + up * .75])); ctx.lineTo(X([p[0] + .12, p[1] + up * .75]), Y([p[0] + .12, p[1] + up * .75])); ctx.closePath(); ctx.fill(); ctx.stroke(); };
  tooth(sg.upper, 1); tooth(sg.teeth, -1);
  const lx = sg.lip.x, mid = (sg.upper[1] + sg.teeth[1]) / 2, hh = sg.lip.height / 2; ctx.fillStyle = "#d98c84";
  for (const s of [1, -1]) { ctx.beginPath(); ctx.ellipse(X([lx + sg.lip.length / 2, 0]), Y([0, mid + s * (hh + .32)]), sg.lip.length / 2 * k + 4, .34 * k, 0, 0, 7); ctx.fill(); }
  ctx.fillStyle = ink; ctx.beginPath(); ctx.arc(X(sg.C), Y(sg.C), 3, 0, 7); ctx.fill(); ctx.beginPath(); ctx.arc(X(sg.tip), Y(sg.tip), 3, 0, 7); ctx.fill();
  ctx.restore();
  return { X, Y, k };
}
export function drawAreas(ctx, af, { x = 0, y = 0, w = 420, h = 110, max = 12 } = {}) {
  ctx.save(); ctx.fillStyle = "#f6f3ec"; ctx.fillRect(x, y, w, h); ctx.fillStyle = "#7a9cb8";
  ctx.beginPath(); ctx.moveTo(x, y + h); af.xs.forEach((cm, i) => ctx.lineTo(x + cm / af.length * w, y + h - Math.min(1, Math.sqrt(af.As[i] / max)) * h)); ctx.lineTo(x + w, y + h); ctx.closePath(); ctx.fill();
  ctx.fillStyle = "#333"; ctx.font = "11px sans-serif"; ctx.fillText(`glottis   area function (sqrt scale, ${af.length.toFixed(1)} cm)   lips`, x + 4, y + 12); ctx.restore();
}
export function drawSpectrum(ctx, resp, peaks, { x = 0, y = 0, w = 420, h = 110, toHz = 5000 } = {}) {
  ctx.save(); ctx.fillStyle = "#f6f3ec"; ctx.fillRect(x, y, w, h);
  const n = Math.min(resp.mag.length, Math.round(toHz / resp.hzPerBin)); let hi = -1e9; for (let k = 2; k < n; k++) hi = Math.max(hi, resp.mag[k]);
  ctx.strokeStyle = "#8a3b12"; ctx.beginPath(); for (let k = 2; k < n; k++) { const px = x + k / n * w, py = y + h - Math.max(0, (resp.mag[k] - hi + 60) / 60) * (h - 14); k === 2 ? ctx.moveTo(px, py) : ctx.lineTo(px, py); } ctx.stroke();
  ctx.fillStyle = "#333"; ctx.font = "11px sans-serif"; for (const p of peaks) ctx.fillText(p.hz.toFixed(0), x + p.hz / toHz * w - 10, y + 12);
  ctx.restore();
}
