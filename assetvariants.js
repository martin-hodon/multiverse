// THE VARIANT EDITOR (2026-11-06): a creature's COATS and VARIANTS in the asset viewer, one at a time -- picked in the
// bar, shown on the stand, edited at the top of the form. What they are (creatures.js dressed, docs/assets.md "Coats
// and variants"):
//   `coats`     a list the world picks from by seed: each a colour table over the definition's own, with an optional
//               `name` and the `params` it changes ({ "tabby": false }, { "pinto": true })
//   `variants`  named ones the world asks for by name: { "rooster": { "params": {...}, "colors": {...} } }
// The editor works on the document itself, as the form does, and hands every change to `onChange(doc)` (the viewer
// writes the JSON back and rebuilds); a change of shape -- one added, renamed, removed -- also to `onPick(pick)`, so
// the bar's list and the form are made again round what is now picked.
//   pick: null (the definition as it is) | { coat: i } | { variant: name }

const el = (tag, props = {}, ...kids) => { const e = Object.assign(document.createElement(tag), props); e.append(...kids.filter((k) => k !== null && k !== undefined && k !== false)); return e; };
const isHex = (v) => typeof v === "string" && /^#[0-9a-f]{6}$/i.test(v);
const isPlain = (v) => v && typeof v === "object" && !Array.isArray(v);
const COAT_WORDS = new Set(["name", "params", "scale"]);
const tableOf = (doc) => (doc.colors || !doc.c ? "colors" : "c");   // (as creatures.js dressed: `colors`, or the older `c`)

// every coat and variant a document has, for the bar's list: [{ pick, label }]
export function variantList(doc) {
  if (!isPlain(doc)) return [];
  const out = [];
  if (Array.isArray(doc.coats)) doc.coats.forEach((c, i) => {
    const n = Object.keys(c ?? {}).filter((k) => !COAT_WORDS.has(k) && !k.startsWith("_")).length + Object.keys(c?.params ?? {}).length + (typeof c?.scale === "number" ? 1 : 0);
    out.push({ pick: { coat: i }, label: `coat ${i + 1}` + (c?.name ? ` · ${c.name}` : "") + (n ? "" : " (as base)") });
  });
  if (isPlain(doc.variants)) for (const k of Object.keys(doc.variants)) out.push({ pick: { variant: k }, label: `variant · ${k}` });
  return out;
}
export const pickKey = (p) => (p == null ? "" : "coat" in p ? "c" + p.coat : "v" + p.variant);
export const pickOf = (key) => (!key ? null : key[0] === "c" ? { coat: +key.slice(1) } : { variant: key.slice(1) });
// does the pick still name something in the document (a coat removed in the JSON: back to the base)
export const pickValid = (doc, p) => p == null || ("coat" in p ? Array.isArray(doc?.coats) && p.coat >= 0 && p.coat < doc.coats.length : isPlain(doc?.variants?.[p.variant]));
// the pick as creatures.js dressed takes it
export const dressArgs = (p) => (p == null ? {} : "coat" in p ? { coat: p.coat } : { variant: p.variant });

// a colour field: the swatch of what the base has under it (click: take it back to that), the picker, the text
function colourRow(key, get, set, base, onRemove) {
  const v = get();
  const t = el("input", { type: "text", value: v, className: "ftext short" }), c = el("input", { type: "color", value: isHex(v) ? v : "#808080" });
  c.oninput = () => { t.value = c.value; set(c.value); };
  t.onchange = () => { if (isHex(t.value)) { c.value = t.value; set(t.value); } };
  const sw = el("span", { className: "vbase", title: base ? `the base: ${base}` : "not in the base's colours" });
  sw.style.background = isHex(base) ? base : "transparent";
  if (!base) sw.classList.add("none");
  return el("div", { className: "frow" }, el("span", { className: "fkey", textContent: key, title: key }), c, t, sw,
            el("button", { className: "vx", textContent: "×", title: `take ${key} out of this one (it falls back to the base)`, onclick: onRemove }));
}
// a param field, by the type of its value: a checkbox, a number, a text
function paramRow(key, get, set, base, onRemove) {
  const v = get(), name = el("span", { className: "fkey", textContent: key, title: key });
  let f;
  if (typeof v === "boolean") { f = el("input", { type: "checkbox", checked: v }); f.onchange = () => set(f.checked); }
  else if (typeof v === "number") { f = el("input", { type: "number", value: v, step: "any", className: "fnum" }); f.onchange = () => { const x = parseFloat(f.value); if (Number.isFinite(x)) set(x); }; }
  else { f = el("input", { type: "text", value: typeof v === "string" ? v : JSON.stringify(v), className: "ftext" }); f.onchange = () => { let x = f.value; try { x = JSON.parse(x); } catch {} set(x); }; }
  return el("div", { className: "frow" }, name, f, el("span", { className: "fdim", textContent: base === undefined ? "" : `base ${JSON.stringify(base)}` }),
            el("button", { className: "vx", textContent: "×", title: `take ${key} out of this one`, onclick: onRemove }));
}
// "add one": a field with the keys it may be (a datalist) and a button; a key not offered can be typed
let lists = 0;
function addRow(label, options, add) {
  const id = "vopts" + lists++, t = el("input", { type: "text", className: "ftext", placeholder: label });
  t.setAttribute("list", id);
  const go = () => { const k = t.value.trim(); if (k) add(k); };
  t.addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
  return el("div", { className: "frow vadd" }, t, el("datalist", { id }, ...options.map((o) => el("option", { value: o }))), el("button", { textContent: "add", onclick: go }));
}
const unique = (name, taken) => { if (!taken.has(name)) return name; for (let i = 2; ; i++) if (!taken.has(`${name} ${i}`)) return `${name} ${i}`; };

// THE PANEL: what is picked (or, at the base, what there is and how to add one), for the top of the form.
//   doc       the document (edited in place)
//   pick      what is picked
//   base      { colors, params }: the definition's own, its frame's merged in (what a coat is laid over)
//   onChange  (doc) after any change; onPick(pick) after a change of shape (made again round it)
export function variantPanel(doc, pick, { base = {}, onChange, onPick }) {
  const box = el("div", { className: "vpanel" });
  if (!isPlain(doc)) return box;
  const table = tableOf(doc), baseCol = { ...(base.colors ?? {}), ...(doc[table] ?? {}) }, basePar = { ...(base.params ?? {}), ...(doc.params ?? {}) };
  const coats = Array.isArray(doc.coats) ? doc.coats : null, vars = isPlain(doc.variants) ? doc.variants : null;
  const changed = () => onChange(doc), reshape = (p) => { onChange(doc); onPick(p); };
  const newCoat = () => { (doc.coats ??= []).push({ name: unique("coat " + (doc.coats.length + 1), new Set(doc.coats.map((c) => c?.name))) }); reshape({ coat: doc.coats.length - 1 }); };
  const newVariant = () => { const k = unique("variant", new Set(Object.keys(doc.variants ?? {}))); (doc.variants ??= {})[k] = { params: {}, colors: {} }; reshape({ variant: k }); };
  const head = (title, ...btns) => el("div", { className: "vhead" }, el("b", { textContent: title }), el("span", { style: "flex:1" }), ...btns);
  const btn = (text, title, onclick) => el("button", { textContent: text, title, onclick });
  if (!pick || !pickValid(doc, pick)) {
    box.append(head("variants"),
      el("div", { className: "fnote", textContent: `${coats?.length ?? 0} coats (the world picks one by seed), ${vars ? Object.keys(vars).length : 0} named variants (asked for by name). ` +
        "Pick one in the bar to see it and edit it here; or add one." }),
      el("div", { className: "frow" }, btn("+ coat", "a new coat: the base's colours, to change", newCoat), btn("+ variant", "a new named variant: params and colours", newVariant)));
    return box;
  }
  const isCoat = "coat" in pick, o = isCoat ? coats[pick.coat] ?? (coats[pick.coat] = {}) : vars[pick.variant];
  // its colours and params, wherever this kind keeps them (a coat: the colours in itself; a variant: under `colors`)
  const colours = isCoat ? o : (o.colors ??= {});
  const colourKeys = () => Object.keys(colours).filter((k) => !(isCoat && COAT_WORDS.has(k)) && !k.startsWith("_"));
  const params = () => (o.params ??= {});
  // ---- the title: what it is, and what can be done to it
  let armed = false;
  const del = btn("delete", "take this one out of the asset (click twice)", () => {
    if (!armed) { armed = true; del.textContent = "delete? again"; del.classList.add("armed"); setTimeout(() => { armed = false; del.textContent = "delete"; del.classList.remove("armed"); }, 2500); return; }
    if (isCoat) { coats.splice(pick.coat, 1); if (!coats.length) delete doc.coats; reshape(coats.length ? { coat: Math.min(pick.coat, coats.length - 1) } : null); }
    else { delete vars[pick.variant]; if (!Object.keys(vars).length) delete doc.variants; reshape(null); }
  });
  const dup = btn("duplicate", "a copy of this one, after it, to change", () => {
    const copy = structuredClone(o);
    if (isCoat) { copy.name = unique((o.name ?? `coat ${pick.coat + 1}`) + " copy", new Set(coats.map((c) => c?.name))); coats.splice(pick.coat + 1, 0, copy); reshape({ coat: pick.coat + 1 }); }
    else { const k = unique(pick.variant + " copy", new Set(Object.keys(vars))); doc.variants = Object.fromEntries(Object.entries(vars).flatMap(([a, b]) => a === pick.variant ? [[a, b], [k, copy]] : [[a, b]])); reshape({ variant: k }); }
  });
  const move = (d) => btn(d < 0 ? "↑" : "↓", d < 0 ? "earlier in the list (the seed's picks follow the order)" : "later in the list", () => {
    const j = pick.coat + d; if (j < 0 || j >= coats.length) return;
    [coats[pick.coat], coats[j]] = [coats[j], coats[pick.coat]]; reshape({ coat: j });
  });
  box.append(head(isCoat ? `coat ${pick.coat + 1} of ${coats.length}` : "variant", ...(isCoat ? [move(-1), move(1)] : []), dup, del));
  // ---- its name (a coat's optional `name`; a variant's key: renamed in place, its order kept)
  const nameIn = el("input", { type: "text", className: "ftext", value: isCoat ? o.name ?? "" : pick.variant, placeholder: isCoat ? "(no name)" : "" });
  nameIn.onchange = () => {
    const n = nameIn.value.trim();
    if (isCoat) { if (n) o.name = n; else delete o.name; reshape(pick); return; }
    if (!n || n === pick.variant) { nameIn.value = pick.variant; return; }
    if (vars[n]) { nameIn.value = pick.variant; nameIn.title = `there is a variant "${n}" already`; return; }
    doc.variants = Object.fromEntries(Object.entries(vars).map(([a, b]) => [a === pick.variant ? n : a, b]));
    reshape({ variant: n });
  };
  box.append(el("div", { className: "frow" }, el("span", { className: "fkey", textContent: "name" }), nameIn));
  if (!isCoat) box.append(el("div", { className: "fnote", textContent: "(the game asks for a variant by this name: renaming one it uses -- the rooster, the peacock's display -- loses it there)" }));
  // ---- its size: `scale`, the whole creature at that share of the base's (built, then scaled: the lioness's .8); empty = the base's
  const sizeIn = el("input", { type: "number", step: "0.01", min: "0.1", className: "fnum", value: typeof o.scale === "number" ? o.scale : "", placeholder: "1" });
  sizeIn.onchange = () => { const x = parseFloat(sizeIn.value); if (Number.isFinite(x) && x > 0 && x !== 1) o.scale = x; else { delete o.scale; sizeIn.value = ""; } changed(); };
  box.append(el("div", { className: "frow" }, el("span", { className: "fkey", textContent: "size ×", title: "scale: the whole creature at this share of the base's size" }), sizeIn,
                el("span", { className: "fdim", textContent: "of the base's (empty: as the base)" })));
  // ---- the colours it changes, each against the base's
  const cs = el("div", { className: "vsec" }, el("div", { className: "vsub", textContent: "colours over the base" }));
  for (const k of colourKeys()) cs.append(colourRow(k, () => colours[k], (v) => { colours[k] = v; changed(); }, baseCol[k], () => { delete colours[k]; reshape(pick); }));
  if (!colourKeys().length) cs.append(el("div", { className: "fdim", textContent: "(none: the base's own)" }));
  // (offered: the base's colour keys, and any other coat's or variant's -- a horse's `pastern`, `blaze`)
  const known = new Set(Object.keys(baseCol));
  for (const c of coats ?? []) for (const k of Object.keys(c ?? {})) if (!COAT_WORDS.has(k) && !k.startsWith("_")) known.add(k);
  for (const v of Object.values(vars ?? {})) for (const k of Object.keys(v?.colors ?? {})) known.add(k);
  cs.append(addRow("add a colour (a key of the base's, or a new one)", [...known].filter((k) => !(k in colours)).sort(), (k) => {
    if (isCoat && COAT_WORDS.has(k)) return;
    colours[k] = isHex(baseCol[k]) ? baseCol[k] : "#808080"; reshape(pick);
  }));
  // ---- the params it changes (its other attributes: a rooster's comb, a black cat's stripes off, a pinto's patches)
  const ps = el("div", { className: "vsec" }, el("div", { className: "vsub", textContent: "params over the base" }));
  const pk = Object.keys(o.params ?? {});
  for (const k of pk) ps.append(paramRow(k, () => params()[k], (v) => { params()[k] = v; changed(); }, basePar[k], () => { delete params()[k]; if (!Object.keys(params()).length) delete o.params; reshape(pick); }));
  if (!pk.length) ps.append(el("div", { className: "fdim", textContent: "(none: the base's own)" }));
  ps.append(addRow("add a param (one of the base's)", Object.keys(basePar).filter((k) => !pk.includes(k)).sort(), (k) => {
    const b = basePar[k];
    params()[k] = typeof b === "boolean" ? !b : b ?? 0; reshape(pick);
  }));
  box.append(cs, ps, el("div", { className: "frow" }, btn("+ coat", "a new coat: the base's colours, to change", newCoat), btn("+ variant", "a new named variant: params and colours", newVariant)));
  return box;
}
