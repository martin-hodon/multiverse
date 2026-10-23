// THE ASSET FORM (2026-10-03): any definition's JSON as a form -- the asset viewer's friendlier face on the same text.
// Nothing about a kind of asset is known here: the form is read from the values themselves, so every definition
// (a creature, a building, a hairstyle, a palette) gets one.
//   number      a number field; drag its label sideways to scrub it (Shift: ten times finer)
//   "#rrggbb"   a colour picker beside its text
//   string      a text field          true / false   a checkbox
//   [n, n, ..]  a short list of numbers (up to 6): fields in a row
//   { .. } [..] a section that opens, its fields made only when it is first opened (a building has hundreds)
//   "_about"..  keys starting with "_" are notes: shown under their section's title, edited in the JSON
//   a string the caller has SUGGESTIONS for (`suggest(key, value)`: a material, a pattern, a palette, an asset's path)
//               offers them as you type
// Every change edits the document in place and calls `onChange(doc)`; the JSON stays the truth -- the viewer
// writes it back into the text.

const el = (tag, props = {}, ...kids) => { const e = Object.assign(document.createElement(tag), props); e.append(...kids.filter((k) => k !== null && k !== undefined)); return e; };
const isHex = (v) => typeof v === "string" && /^#[0-9a-f]{6}$/i.test(v);
const isNums = (v) => Array.isArray(v) && v.length > 0 && v.length <= 6 && v.every((x) => typeof x === "number");
const stepOf = (v) => { const a = Math.abs(v); return Number.isInteger(v) && a >= 2 ? 1 : a === 0 ? .01 : Math.pow(10, Math.floor(Math.log10(a)) - 1); };
const round = (v, st) => +(Math.round(v / st) * st).toFixed(Math.max(0, -Math.floor(Math.log10(st)) + 1));

// a number field with a scrubbing label: drag left/right to change it
function numberField(get, set, label) {
  const inp = el("input", { type: "number", value: get(), step: "any", className: "fnum" });
  inp.addEventListener("change", () => { const v = parseFloat(inp.value); if (Number.isFinite(v)) set(v); });
  if (label) {
    label.classList.add("scrub");
    label.title = "drag sideways to change (Shift: finer)";
    label.addEventListener("pointerdown", (e) => {
      const v0 = get(), x0 = e.clientX, st = stepOf(v0 || .1);
      label.setPointerCapture(e.pointerId);
      const move = (m) => { const v = round(v0 + (m.clientX - x0) * st * (m.shiftKey ? .1 : 1), st * (m.shiftKey ? .1 : 1)); inp.value = v; set(v); };
      const up = () => { label.removeEventListener("pointermove", move); label.removeEventListener("pointerup", up); };
      label.addEventListener("pointermove", move); label.addEventListener("pointerup", up);
    });
  }
  return inp;
}

let SUGGEST = null, lists = 0;
function fieldFor(obj, key, onChange) {
  const v = obj[key], set = (x) => { obj[key] = x; onChange(); };
  const name = el("span", { className: "fkey", textContent: key });
  if (typeof v === "number") return el("div", { className: "frow" }, name, numberField(() => obj[key], set, name));
  if (typeof v === "boolean") { const c = el("input", { type: "checkbox", checked: v }); c.onchange = () => set(c.checked); return el("div", { className: "frow" }, name, c); }
  if (isHex(v)) {
    const t = el("input", { type: "text", value: v, className: "ftext short" }), c = el("input", { type: "color", value: v });
    c.oninput = () => { t.value = c.value; set(c.value); };
    t.onchange = () => { if (isHex(t.value)) { c.value = t.value; set(t.value); } };
    return el("div", { className: "frow" }, name, c, t);
  }
  if (typeof v === "string") {
    const t = el("input", { type: "text", value: v, className: "ftext" }); t.onchange = () => set(t.value);
    const opts = SUGGEST?.(String(key), v);
    if (opts?.length) { const id = "fsug" + lists++, dl = el("datalist", { id }, ...opts.map((o) => el("option", { value: o }))); t.setAttribute("list", id); return el("div", { className: "frow" }, name, t, dl); }
    return el("div", { className: "frow" }, name, t);
  }
  if (v === null) return el("div", { className: "frow" }, name, el("span", { className: "fnull", textContent: "null (edit in JSON)" }));
  if (isNums(v)) return el("div", { className: "frow" }, name, el("span", { className: "fnums" }, ...v.map((_, i) => numberField(() => v[i], (x) => { v[i] = x; onChange(); }))));
  return section(key, v, onChange);
}

// a section: an object's or a list's fields, made when first opened
function section(key, v, onChange, open = false) {
  const n = Array.isArray(v) ? v.length : Object.keys(v).filter((k) => !k.startsWith("_")).length;
  const sum = el("summary", {}, el("span", { className: "fkey" }, key), el("span", { className: "fdim", textContent: Array.isArray(v) ? ` [${n}]` : ` {${n}}` }));
  const d = el("details", { className: "fsec" }, sum);
  let made = false;
  const make = () => {
    if (made) return; made = true;
    fill(d, v, onChange);
  };
  d.addEventListener("toggle", () => { if (d.open) make(); });
  if (open) { d.open = true; make(); }
  return d;
}

function fill(box, v, onChange) {
  if (Array.isArray(v)) { v.forEach((_, i) => box.append(fieldFor(v, i, onChange))); return; }
  const notes = Object.keys(v).filter((k) => k.startsWith("_") && typeof v[k] === "string");
  for (const k of notes) box.append(el("div", { className: "fnote", textContent: (k === "_about" ? "" : k.slice(1) + ": ") + v[k] }));
  for (const k of Object.keys(v)) if (!k.startsWith("_")) box.append(fieldFor(v, k, onChange));
}

// the whole document's form into `root` (replacing what was there); returns nothing -- changes go to onChange(doc)
export function buildForm(root, doc, onChange, { suggest = null } = {}) {
  SUGGEST = suggest;
  root.replaceChildren();
  if (doc === null || typeof doc !== "object") { root.append(el("div", { className: "fnote", textContent: "(not an object: edit it in the JSON)" })); return; }
  const changed = () => onChange(doc);
  const notes = Object.keys(doc).filter((k) => k.startsWith("_") && typeof doc[k] === "string");
  for (const k of notes) root.append(el("div", { className: "fnote", textContent: doc[k] }));
  // the plain fields first, then the sections -- and a document's `params` opened at once (what one tunes most)
  const keys = Object.keys(doc).filter((k) => !k.startsWith("_"));
  const plain = keys.filter((k) => doc[k] === null || typeof doc[k] !== "object" || isNums(doc[k]));
  for (const k of plain) root.append(fieldFor(doc, k, changed));
  for (const k of keys.filter((k) => !plain.includes(k))) root.append(section(k, doc[k], changed, k === "params"));
}
