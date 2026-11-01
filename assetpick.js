// THE PICKER (docs/assets.md): a family of paintings or patterns is listed, and only the one picked is generated: a sheet of all of
// them took as long as all of them. Under the list, what can be asked of that one (its seed, its colouring, its size...), and
// Regenerate. A choice stays until another item is picked; left empty a field means the item's own value, shown greyed in it.
const kept = new Map();            // (each document's: the item and what's asked of it)
const el = (tag, props = {}, ...kids) => { const e = Object.assign(document.createElement(tag), props); e.append(...kids); return e; };

// items: [[key, label]]; fields(key): [{ key, label, own, options?: [[value, label]], text? }]; go(): generate, the state as it stands
//   -> { key, values } for the item to draw now
export function showPick(panel, path, { items, fields, go, seeded = "seed" }) {
  let S = kept.get(path);
  if (!S || !items.some(([k]) => k === S.key)) kept.set(path, S = { key: items[0][0], values: {}, filter: "" });
  const list = fields(S.key), sign = JSON.stringify([path, S.key, items, list]);
  if (panel.dataset.sign !== sign) {
    panel.dataset.sign = sign;
    const scroll = panel.querySelector(".items")?.scrollTop ?? 0;
    const rows = el("div", { className: "items" });
    const fill = () => {
      rows.replaceChildren(...items.filter(([, l]) => l.toLowerCase().includes(S.filter.toLowerCase())).map(([k, l]) => {
        const b = el("button", { className: k === S.key ? "on" : "", textContent: l, title: l });
        b.onclick = () => { S.key = k; S.values = {}; go(); };
        return b;
      }));
    };
    fill();
    const find = el("input", { type: "search", placeholder: `find · ${items.length}`, value: S.filter });
    find.oninput = () => { S.filter = find.value; fill(); };
    const inputs = {}, ask = el("div", { className: "ask" });
    for (const f of list) {
      const box = f.options
        ? el("select", {}, el("option", { value: "", textContent: `(own${f.own !== undefined ? `: ${f.own}` : ""})` }), ...f.options.map(([v, l]) => el("option", { value: v, textContent: l })))
        : el("input", { type: f.text ? "text" : "number", placeholder: String(f.own ?? ""), step: "any" });
      box.value = S.values[f.key] ?? "";
      box.oninput = () => { S.values[f.key] = box.value; };
      box.onkeydown = (e) => { e.stopPropagation(); if (e.key === "Enter") go(); };
      inputs[f.key] = box;
      ask.append(el("label", { title: f.key }, el("span", { textContent: f.label ?? f.key }), box));
    }
    const redo = el("button", { className: "go", textContent: "Regenerate" });
    redo.onclick = go;
    const buttons = el("div", { className: "acts" }, redo);
    if (inputs[seeded]) {
      const other = el("button", { textContent: "New seed", title: "another seed, and generate" });
      other.onclick = () => { inputs[seeded].value = S.values[seeded] = String(1 + Math.floor(Math.random() * 9999)); go(); };
      buttons.append(other);
    }
    panel.replaceChildren(find, rows, ask, buttons);
    rows.scrollTop = scroll;
    find.onkeydown = (e) => e.stopPropagation();
  }
  panel.style.display = "flex";
  return S;
}

// a value asked for: a number where it reads as one, else undefined for "the item's own"
export const asked = (S, k) => S.values[k] === undefined || S.values[k] === "" ? undefined : isNaN(+S.values[k]) ? S.values[k] : +S.values[k];

// what's generated, into the sheet: whole and fitted if it's a panel, two tiles across if it repeats
export function drawPicked(cv, source, { repeat = false, w, h }) {
  const iw = source.width, ih = source.height;
  if (repeat) {
    const side = Math.min(w, h), k = side / 2 / iw;
    cv.width = side; cv.height = Math.round(side * ih / iw);
    const g = cv.getContext("2d", { willReadFrequently: true }), f = g.createPattern(source, "repeat");
    f.setTransform(new DOMMatrix([k, 0, 0, k, 0, 0]));
    g.fillStyle = f; g.fillRect(0, 0, cv.width, cv.height);
    return;
  }
  const k = Math.min(w / iw, h / ih);
  cv.width = Math.max(1, Math.round(iw * k)); cv.height = Math.max(1, Math.round(ih * k));
  const g = cv.getContext("2d", { willReadFrequently: true });
  g.imageSmoothingQuality = "high";
  g.drawImage(source, 0, 0, cv.width, cv.height);
}
