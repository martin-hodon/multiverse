// THE ASSET MANAGER'S SECTIONS, PARTS AND LAYERS (assets.html) -- as the atlas has them (/home/martin/store/apps/atlas
// js/main.js: state.cuts, isolate, the layers' sliders), for what is on the stand.
//
//   CUTS     three axis-aligned section planes (x, y, z) through the asset, each switched on, slid across the asset's box
//            and flipped (which side is kept) -- the renderer's clipping (a THREE.ClippingGroup: the stand). The three
//            planes are always there, an unused one far off, so switching one compiles nothing. The cut faces are CAPPED:
//            every opaque mesh's back faces drawn again in one flat colour after it -- a closed solid cut open shows its
//            inside's back faces exactly where the section is, so the section reads as solid stone (the walls of a floor
//            plan). "face" turns the eye square onto the cut.
//   PARTS    (a building) a click picks the part under the pointer -- a top-level part of the definition's `build` (a
//            component's pieces are its part's), or with "pieces" the assembly's own part ("church/high roof"). Frame
//            flies to it, isolate shows it alone (and flies), hide hides it; show all brings everything back. The list
//            shows every part with a box to hide it; JSON selects its definition in the editor.
//   LAYERS   (a building) every triangle sorted into a layer -- roofs, outer walls, inner walls, floors, ceilings &
//            vaults, stairs, windows & glass, doors, ornament, furniture -- each with an opacity: 0 hides it, under 1 it is
//            see-through (no depth written).
//
// THE BUILDING IS DRAWN AS THE GAME DRAWS IT: one mesh per finish rule, every part's triangles merged (architecture.js
// finishMeshes / bakeArch), so which part a triangle came from is gone. It is found again here, only when parts or
// layers are first asked for ("exploding" the building): every triangle of every drawn mesh is looked up among the
// assembly's own triangles (a piece of a finish is cut out of exactly one of them, in its plane), and the meshes are
// split by (part, layer), each in a copy of its material whose opacity the layer's slider drives. Nothing in the game's
// code is changed for it.
import * as THREE from "three";
import { uniform } from "three/tsl";
import { interiorsOf, inInterior } from "./arch/finish.js";

export const LAYERS = [
  ["roofs", "roofs", "the outside of roofs and domes"],
  ["outer", "outer walls", "walls (and piers, buttresses, columns) facing the open air"],
  ["inner", "inner walls", "walls facing an interior (the building's `interior` spaces)"],
  ["floors", "floors", "every face looking up that is not a roof: floors, terraces, platforms, the ground"],
  ["ceilings", "ceilings & vaults", "faces looking down, vaults, ribs, a roof's or a dome's underside"],
  ["stairs", "stairs", "flights, staircases, spiral stairs, steps, railings"],
  ["windows", "windows & glass", "panes and tracery"],
  ["doors", "doors", "the door leaves (assets/doors)"],
  ["ornament", "ornament", "mouldings, wimpergs, pinnacles, finials, cresting"],
  ["furniture", "furniture", "the items a building is furnished with"],
];
const LI = Object.fromEntries(LAYERS.map(([k], i) => [k, i]));
const STAIRS = new Set(["flight", "staircase", "steps", "spiral-stair", "crepidoma", "railing", "stair"]);
const ORNAMENT = new Set(["moulding", "wimperg", "pinnacle", "finial", "cresting", "statue", "iron", "lace", "crocket", "frieze"]);
const ROOFS = new Set(["roof", "dome", "spire", "kokoshnik"]);
const VAULTS = new Set(["vault", "groin", "ribs", "pendentives", "ceiling"]);
const AX = ["x", "y", "z"], CAP = 0x9b4632, HOT = 0xd9a441;

const css = `
#av { position:absolute; right:6px; top:6px; width:300px; max-height:calc(100% - 12px); overflow:auto; display:flex; flex-direction:column; gap:4px; z-index:3;
      background:var(--panel); border:1px solid var(--line); border-radius:4px; padding:5px; font:12px/1.4 ui-monospace,Menlo,Consolas,monospace; }
#av .tabs { display:flex; gap:3px; } #av .tabs button { flex:1; padding:2px 4px; }
#av button.on { color:var(--hot); border-color:var(--hot); }
#av section { flex:none; display:flex; flex-direction:column; gap:3px; padding-top:3px; border-top:1px solid var(--line); }
#av .row { display:grid; grid-template-columns:16px 12px 1fr 64px 26px 40px; align-items:center; gap:3px; }
#av .row input[type=range], #av .lrow input[type=range] { width:100%; min-width:0; margin:0; }
#av .num { color:var(--dim); text-align:right; font-size:11px; }
#av .lrow { display:grid; grid-template-columns:128px 1fr 30px; align-items:center; gap:4px; }
#av .lrow span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--ink); }
#av .lrow.none span { color:var(--dim); }
#av .acts { display:flex; gap:3px; flex-wrap:wrap; } #av .acts button { padding:1px 6px; }
#av .sel { color:var(--hot); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#av .note { color:var(--dim); font-size:11px; }
#av .list { overflow:auto; max-height:220px; min-height:40px; border:1px solid var(--line); border-radius:3px; background:#1e2126; }
#av .list div { display:flex; align-items:center; gap:3px; padding:0 3px; }
#av .list div.on { background:#2f343b; }
#av .list button { border:0; background:none; padding:0 2px; text-align:left; flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#av .list .n { color:var(--dim); font-size:10px; }
#av input[type=search], #av select { font:inherit; min-width:0; background:#1e2126; color:var(--ink); border:1px solid var(--line); border-radius:3px; padding:1px 4px; }
`;

// stand: a THREE.ClippingGroup holding everything shown; boxOf(): the asset's box (Box3) as the view frames it;
// reveal(name): the editor shows that part's definition
export function createArchView({ stand, camera, nav, canvas, host, boxOf, reveal }) {
  document.head.append(Object.assign(document.createElement("style"), { textContent: css }));
  const el = (tag, props = {}, ...kids) => { const e = Object.assign(document.createElement(tag), props); e.append(...kids); return e; };

  // ---- state --------------------------------------------------------------------------------------------------------
  const cuts = AX.map((_, i) => ({ on: false, at: 0, flip: false, i }));
  let caps = true, box = new THREE.Box3(), path = null, open = { cuts: false, parts: false, layers: false };
  const layerVal = LAYERS.map(() => 1), layerU = LAYERS.map(() => uniform(1));
  // the building on the stand, and what exploding it found
  let B = null;          // { root, doors, asm, def, path }
  let X = null;          // { group, subs: [mesh], pieces: [{ name, top, tris }], tops: [{ name, pieces: [i], tris }], mats: Map }
  let level = "part", selected = null, isolated = null;   // selected / isolated: { level, key } -- key a top index or a piece index
  const hidden = new Set();   // piece indices
  const planes = AX.map(() => new THREE.Plane(new THREE.Vector3(0, 1, 0), 1e7));
  stand.clippingPlanes = planes;   // (union: a point on the wrong side of any one is cut away)
  const capMat = new THREE.MeshBasicNodeMaterial({ color: CAP, side: THREE.BackSide });
  const hiMat = new THREE.MeshBasicNodeMaterial({ color: HOT, transparent: true, opacity: .42, depthWrite: false, side: THREE.DoubleSide,
                                                  polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });

  // ---- the panel ----------------------------------------------------------------------------------------------------
  const tabs = { cuts: el("button", { textContent: "cuts", title: "section planes through the asset (as the atlas's)" }),
                 parts: el("button", { textContent: "parts", title: "click the building to pick a part: frame it, isolate it, hide it" }),
                 layers: el("button", { textContent: "layers", title: "roofs, walls, floors... each with its opacity" }) };
  const secs = { cuts: el("section"), parts: el("section"), layers: el("section") };
  const panel = el("div", { id: "av" }, el("div", { className: "tabs" }, tabs.cuts, tabs.parts, tabs.layers), secs.cuts, secs.parts, secs.layers);
  host.append(panel);
  for (const k of Object.keys(tabs)) tabs[k].onclick = () => { open[k] = !open[k]; if (open[k] && k !== "cuts") explode(); paint(); };

  // CUTS
  const cutRows = cuts.map((c) => {
    const on = el("input", { type: "checkbox", title: `cut along ${AX[c.i]}` }), r = el("input", { type: "range", min: 0, max: 1000, step: 1 });
    const num = el("span", { className: "num" }), flip = el("button", { textContent: "⇄", title: "keep the other side" }), face = el("button", { textContent: "face", title: "look square at the cut" });
    on.onchange = () => { c.on = on.checked; if (c.on) faceCut(c.i); update(); };
    r.oninput = () => { c.at = box.min.getComponent(c.i) + (box.max.getComponent(c.i) - box.min.getComponent(c.i)) * r.value / 1000; if (!c.on) { c.on = on.checked = true; faceCut(c.i); } update(); };
    flip.onclick = () => { c.flip = !c.flip; if (c.on) faceCut(c.i); update(); };
    face.onclick = () => faceCut(c.i);
    secs.cuts.append(el("div", { className: "row" }, on, el("b", { textContent: AX[c.i] }), r, num, flip, face));
    return { on, r, num, flip };
  });
  const capBox = el("input", { type: "checkbox", checked: true });
  capBox.onchange = () => { caps = capBox.checked; update(); };
  const cutReset = el("button", { textContent: "no cuts" });
  cutReset.onclick = () => { for (const c of cuts) { c.on = false; c.flip = false; c.at = mid(c.i); } update(); };
  secs.cuts.append(el("div", { className: "acts" }, el("label", { title: "fill the cut faces (an opaque mesh's back faces in one colour)" }, capBox, " caps"), cutReset),
                   el("div", { className: "note", textContent: "default keeps the low side (below y, -x, -z); ⇄ keeps the other" }));

  // PARTS
  const levelSel = el("select", { title: "what a click picks: a part of the definition's build list, or the assembly's own piece" });
  levelSel.append(new Option("parts (build list)", "part"), new Option("pieces (assembly)", "piece"));
  levelSel.onchange = () => { level = levelSel.value; selected = null; isolated = null; refresh(); };
  const selName = el("div", { className: "sel", textContent: "click the building to pick a part" });
  const selNote = el("div", { className: "note" });
  const bFrame = el("button", { textContent: "frame", title: "fly to it" }), bIso = el("button", { textContent: "isolate", title: "show it alone (and fly to it)" });
  const bHide = el("button", { textContent: "hide" }), bJson = el("button", { textContent: "JSON", title: "its definition, in the editor" }), bAll = el("button", { textContent: "show all" });
  const find = el("input", { type: "search", placeholder: "filter parts" }), list = el("div", { className: "list" });
  secs.parts.append(levelSel, selName, selNote, el("div", { className: "acts" }, bFrame, bIso, bHide, bJson, bAll), find, list);
  bFrame.onclick = () => selected && flyTo(piecesOf(selected));
  bIso.onclick = () => { if (!selected) return; isolated = isolated ? null : { ...selected }; refresh(); if (isolated) flyTo(piecesOf(isolated)); };
  bHide.onclick = () => { if (!selected) return; for (const p of piecesOf(selected)) hidden.add(p); if (isolated && same(isolated, selected)) isolated = null; selected = null; refresh(); };
  bAll.onclick = () => { hidden.clear(); isolated = null; refresh(); };
  bJson.onclick = () => { if (selected && X) reveal?.(level === "part" ? X.tops[selected.key].name : X.pieces[selected.key].top); };
  find.oninput = () => paintList();

  // LAYERS
  const layerRows = LAYERS.map(([k, label, title], i) => {
    const r = el("input", { type: "range", min: 0, max: 1, step: .05, value: 1 }), num = el("span", { className: "num", textContent: "1" });
    r.oninput = () => setLayer(i, +r.value);
    const row = el("div", { className: "lrow", title }, el("span", { textContent: label }), r, num);
    secs.layers.append(row);
    return { r, num, row };
  });
  const lAll = el("button", { textContent: "all 1" }), lPlan = el("button", { textContent: "no roofs", title: "roofs and ceilings off: see down into the rooms" }),
        lShell = el("button", { textContent: "x-ray walls", title: "outer walls and roofs see-through" });
  lAll.onclick = () => LAYERS.forEach((_, i) => setLayer(i, 1));
  lPlan.onclick = () => { setLayer(LI.roofs, 0); setLayer(LI.ceilings, 0); };
  lShell.onclick = () => { setLayer(LI.roofs, .15); setLayer(LI.outer, .25); };
  secs.layers.append(el("div", { className: "acts" }, lAll, lPlan, lShell));

  function paint() {
    for (const k of Object.keys(tabs)) {
      tabs[k].classList.toggle("on", open[k]);
      secs[k].style.display = open[k] && (k === "cuts" || B) ? "flex" : "none";
    }
    tabs.parts.style.display = tabs.layers.style.display = B ? "" : "none";
    cuts.forEach((c, i) => {
      const R = cutRows[i], lo = box.min.getComponent(i), hi = box.max.getComponent(i);
      R.on.checked = c.on; R.r.value = hi > lo ? Math.round((c.at - lo) / (hi - lo) * 1000) : 500;
      R.num.textContent = c.at.toFixed(2) + " m"; R.flip.classList.toggle("on", c.flip);
    });
    capBox.checked = caps;
    layerRows.forEach((R, i) => { R.r.value = layerVal[i]; R.num.textContent = layerVal[i].toFixed(2).replace(/\.?0+$/, "") || "0";
      R.row.classList.toggle("none", !!X && !X.layerTris[i]); R.row.title = LAYERS[i][2] + (X ? ` -- ${X.layerTris[i].toLocaleString()} triangles` : ""); });
    levelSel.value = level;
    if (selected && X) {
      const pcs = piecesOf(selected), n = pcs.reduce((a, p) => a + X.pieces[p].tris, 0);
      const top = level === "part" ? X.tops[selected.key] : X.tops[X.pieces[selected.key].topIndex];
      selName.textContent = level === "part" ? top.name : X.pieces[selected.key].name;
      const type = B.def.parts?.[top.name]?.type;
      selNote.textContent = (level === "piece" ? `of ${top.name} · ` : `${pcs.length} pieces · `) + (type ? `type ${type} · ` : "") + `${n.toLocaleString()} triangles` +
        (level === "piece" ? ` · kind ${X.pieces[selected.key].kind}` : "");
    } else { selName.textContent = X ? "click the building to pick a part" : "..."; selNote.textContent = isolated ? "isolated: one part shown" : ""; }
    bIso.textContent = isolated ? "show the rest" : "isolate";
    for (const b of [bFrame, bHide, bJson]) b.disabled = !selected;
    bIso.disabled = !selected && !isolated;
    paintList();
  }
  // the list: every part (or piece) with triangles, a box to hide it, its name to pick it
  function paintList() {
    if (!X || !open.parts) { list.replaceChildren(); return; }
    const words = find.value.toLowerCase().split(/\s+/).filter(Boolean);
    const items = level === "part" ? X.tops.map((t, i) => [i, t.name, t.tris, t.pieces]) : X.pieces.map((p, i) => [i, p.name, p.tris, [i]]);
    const rows = [];
    for (const [i, name, tris, pcs] of items) {
      if (!tris || !words.every((w) => name.toLowerCase().includes(w))) continue;
      const shown = pcs.some((p) => !hidden.has(p));
      const cb = el("input", { type: "checkbox", checked: shown, title: shown ? "hide it" : "show it" });
      cb.onchange = () => { for (const p of pcs) cb.checked ? hidden.delete(p) : hidden.add(p); refresh(); };
      const b = el("button", { textContent: name, title: name }); b.onclick = () => { selected = { level, key: i }; refresh(); };
      const row = el("div", {}, cb, b, el("span", { className: "n", textContent: tris.toLocaleString() }));
      if (selected && selected.key === i) row.classList.add("on");
      rows.push(row);
      if (rows.length > 600) break;
    }
    list.replaceChildren(...rows);
  }

  // ---- cuts ---------------------------------------------------------------------------------------------------------
  const mid = (i) => (box.min.getComponent(i) + box.max.getComponent(i)) / 2;
  function update() {
    cuts.forEach((c, i) => {
      const n = new THREE.Vector3(); n.setComponent(i, c.flip ? 1 : -1);
      // (kept where n.p + constant >= 0: the default keeps p <= at -- below a level cut, the plan seen from above)
      if (c.on) planes[i].set(n, c.flip ? -c.at : c.at); else planes[i].set(new THREE.Vector3(0, 1, 0), 1e7);
    });
    syncCaps();
    paint();
  }
  const anyCut = () => cuts.some((c) => c.on);
  // the eye to the side that has been cut away, square on to the cut (a level cut: from above, a little tilted)
  function faceCut(i) {
    if (box.isEmpty()) return;
    const c = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3()), d = Math.max(size.x, size.y, size.z) * 1.3 + 1, s = cuts[i].flip ? -1 : 1;
    c.setComponent(i, cuts[i].at);
    const from = c.clone();
    if (i === 1) from.add(new THREE.Vector3(0, s * d * .93, d * .37));
    else { from.setComponent(i, cuts[i].at + s * d); from.y += d * .08; }
    nav.fly(nav.poseOf(from, c));
  }
  // CAPS: each opaque mesh's back faces again, flat, drawn after it -- where the cut opens a solid, they are the section
  function syncCaps() {
    const want = caps && anyCut();
    for (const root of roots()) root.traverse((o) => {
      if (!o.isMesh || o.userData.av) return;
      const m = o.material;
      if (!m || Array.isArray(m) || m.userData?.avSrc?.transparent || (m.transparent && !m.userData?.avLayerMat) || m.blending === THREE.AdditiveBlending) return;
      let cap = o.userData.avCap;
      if (!cap && !want) return;
      if (!cap) { cap = o.userData.avCap = new THREE.Mesh(o.geometry, capMat); cap.userData.av = "cap"; cap.renderOrder = 1; cap.raycast = () => {}; o.add(cap); }
      const L = o.userData.avLayer;
      cap.visible = want && (L === undefined || layerVal[L] >= .999);
    });
  }
  const roots = () => [B?.root ?? target, B?.doors].filter(Boolean);
  let target = null;   // (any other asset: cuts only)

  // ---- exploding the building into its parts and layers --------------------------------------------------------------
  function explode() {
    if (!B || X) return;
    const t0 = performance.now();
    const { asm, def } = B;
    // the top-level parts: the build list, every part of the definition, the base -- a piece is its longest name's
    const names = [...new Set([...(def.build ?? []).map((b) => typeof b === "string" ? b : b.part), ...Object.keys(def.parts ?? {}), "base"])];
    const topOf = (nm) => {
      if (names.includes(nm)) return nm;
      let best = null;
      for (const t of names) if ((nm.startsWith(t + " ") || nm.startsWith(t + "/")) && (!best || t.length > best.length)) best = t;
      return best ?? nm.split("/")[0];
    };
    const tops = [], topIdx = new Map();
    const pieces = asm.parts.map((p) => {
      const tn = topOf(p.name);
      if (!topIdx.has(tn)) { topIdx.set(tn, tops.length); tops.push({ name: tn, pieces: [], tris: 0 }); }
      return { name: p.name, kind: p.kind, top: tn, topIndex: topIdx.get(tn), tris: 0 };
    });
    pieces.forEach((p, i) => tops[p.topIndex].pieces.push(i));
    const vols = interiorsOf(asm);
    const look = triangleIndex(asm);
    const layerTris = LAYERS.map(() => 0);
    const mats = new Map();
    const matFor = (src, L) => {
      const k = src.uuid + "|" + L;
      let m = mats.get(k);
      if (!m) {
        m = src.clone();
        m.userData = { ...src.userData, avLayerMat: true, avSrc: { transparent: src.transparent, depthWrite: src.depthWrite, opacity: src.opacity }, avL: L };
        if (m.isNodeMaterial) m.opacityNode = src.opacityNode ? src.opacityNode.mul(layerU[L]) : layerU[L];
        m.wireframe = src.wireframe;
        if (layerVal[L] < .999) { m.transparent = true; m.depthWrite = false; }   // (the layer already faded: a rebuild while it is)
        if (!m.isNodeMaterial) m.opacity = src.opacity * layerVal[L];
        mats.set(k, m);
      }
      return m;
    };
    const group = new THREE.Group(); group.name = "parts and layers";
    const subs = [];
    let unmatched = 0;
    B.root.updateWorldMatrix(true, true);
    const rootInv = B.root.matrixWorld.clone().invert(), rel = (o) => rootInv.clone().multiply(o.matrixWorld);   // (a mesh's place in the building's own frame)
    const split = (o, pieceOf, layerOf) => {
      let geo = o.geometry;
      if (geo.index) geo = geo.toNonIndexed();
      const T = geo.attributes.position.count / 3, keys = new Int32Array(T), by = new Map();
      for (let t = 0; t < T; t++) {
        const pi = pieceOf(geo, t), L = layerOf(geo, t, pi);
        if (pi >= 0) pieces[pi].tris++; else unmatched++;
        layerTris[L]++;
        const k = (pi + 1) * 16 + L; keys[t] = k;
        by.set(k, (by.get(k) ?? 0) + 1);
      }
      const names = Object.keys(geo.attributes);
      for (const [k, n] of by) {
        const g = new THREE.BufferGeometry(), out = {};
        for (const a of names) { const A = geo.attributes[a]; out[a] = new A.array.constructor(n * 3 * A.itemSize); }
        let w = 0;
        for (let t = 0; t < T; t++) {
          if (keys[t] !== k) continue;
          for (const a of names) { const A = geo.attributes[a], s = A.itemSize; out[a].set(A.array.subarray(t * 3 * s, (t + 1) * 3 * s), w * 3 * s); }
          w++;
        }
        for (const a of names) g.setAttribute(a, new THREE.BufferAttribute(out[a], geo.attributes[a].itemSize, geo.attributes[a].normalized));
        g.computeBoundingSphere(); g.computeBoundingBox();
        const pi = Math.floor(k / 16) - 1, L = k % 16;
        const m = new THREE.Mesh(g, matFor(o.material, L));
        m.matrix.copy(rel(o)); m.matrixAutoUpdate = false;   // (in its mesh's place under the building)
        m.userData.avPiece = pi; m.userData.avLayer = L; m.name = o.name;
        subs.push(m); group.add(m);
      }
    };
    const A = new THREE.Vector3(), Bv = new THREE.Vector3(), C = new THREE.Vector3(), cen = new THREE.Vector3(), nrm = new THREE.Vector3();
    const tri = (geo, t) => {
      const P = geo.attributes.position.array, i = t * 9;
      A.set(P[i], P[i + 1], P[i + 2]); Bv.set(P[i + 3], P[i + 4], P[i + 5]); C.set(P[i + 6], P[i + 7], P[i + 8]);
      cen.copy(A).add(Bv).add(C).multiplyScalar(1 / 3);
      nrm.subVectors(Bv, A).cross(C.clone().sub(A)); if (nrm.lengthSq() > 1e-20) nrm.normalize(); else nrm.set(0, 1, 0);
    };
    // the furniture: each copy of an item is its part's (the nearest of the item parts' placings)
    const itemAt = [];
    asm.parts.forEach((p, pi) => { if (p.kind === "item") for (const [, x, y, z] of p.instances) itemAt.push([x, y, z, pi]); });
    const meshes = [];
    B.root.traverse((o) => { if (o.isMesh && !o.userData.av && o.parent?.name !== "parts and layers") meshes.push(o); });
    for (const o of meshes) {
      if (!o.geometry?.attributes?.position) continue;
      if (o.name === "items") {
        split(o, (geo, t) => {
          tri(geo, t);
          let best = -1, bd = Infinity;
          for (const [x, y, z, pi] of itemAt) { const d = (cen.x - x) ** 2 + (cen.y - y) ** 2 * .25 + (cen.z - z) ** 2; if (d < bd) { bd = d; best = pi; } }
          return best;
        }, () => LI.furniture);
      } else {
        split(o, (geo, t) => { tri(geo, t); return look.find(cen, nrm); },
          (geo, t, pi) => pi < 0 ? LI.ornament : LI[classify(asm.parts[pi], look.normalOf, cen, look.origin, vols)]);
      }
      o.visible = false;
    }
    // the doors: each leaf its doorway's part (the stone nearest its middle)
    if (B.doors) B.doors.traverse((o) => {
      if (!o.isMesh || o.userData.av) return;
      o.geometry.computeBoundingBox();
      const c = o.geometry.boundingBox.getCenter(new THREE.Vector3()).applyMatrix4(o.matrixWorld).applyMatrix4(rootInv);
      const pi = look.near(c);
      o.material = matFor(o.material, LI.doors); o.userData.avPiece = pi; o.userData.avLayer = LI.doors;
      const T = (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3;
      if (pi >= 0) pieces[pi].tris += T;
      layerTris[LI.doors] += T;
      subs.push(o);
    });
    for (const t of tops) t.tris = t.pieces.reduce((a, p) => a + pieces[p].tris, 0);
    B.root.add(group);
    X = { group, subs, pieces, tops, mats, layerTris, unmatched, ms: performance.now() - t0 };
    console.debug?.(`archview: ${subs.length} meshes, ${tops.length} parts, ${pieces.length} pieces in ${X.ms.toFixed(0)} ms`);
    // (what was asked of the last building, by name: kept through a rebuild as the definition is typed)
    if (keep) {
      if (keep.hidden) for (const nm of keep.hidden) pieces.forEach((p, i) => { if (p.name === nm) hidden.add(i); });
      const back = (s) => { if (!s) return null; const arr = s.level === "part" ? tops : pieces, k = arr.findIndex((q) => q.name === s.name); return k >= 0 ? { level: s.level, key: k } : null; };
      selected = back(keep.selected); isolated = back(keep.isolated); keep = null;
    }
    refresh();
  }
  let keep = null;

  // what is shown: the layers' opacity, the parts hidden, the one isolated, the one picked (lit)
  function refresh() {
    if (X) {
      const iso = isolated ? new Set(piecesOf(isolated)) : null, sel = selected ? new Set(piecesOf(selected)) : null;
      for (const m of X.subs) {
        const pi = m.userData.avPiece, L = m.userData.avLayer;
        m.visible = layerVal[L] > .001 && !hidden.has(pi) && (!iso || iso.has(pi));
        const lit = !!sel && sel.has(pi);
        if (lit && !m.userData.avHi) { const h = new THREE.Mesh(m.geometry, hiMat); h.userData.av = "hi"; h.renderOrder = 3; h.raycast = () => {}; m.userData.avHi = h; m.add(h); }
        if (m.userData.avHi) m.userData.avHi.visible = lit;
      }
    }
    syncCaps();
    paint();
  }
  function setLayer(i, v) {
    layerVal[i] = v; layerU[i].value = v;
    if (X) for (const m of X.mats.values()) {
      if (m.userData.avL !== i) continue;
      const src = m.userData.avSrc, see = v < .999 || src.transparent;
      if (m.transparent !== see) { m.transparent = see; m.needsUpdate = true; }
      const dw = v < .999 ? false : src.depthWrite;
      if (m.depthWrite !== dw) { m.depthWrite = dw; m.needsUpdate = true; }
      if (!m.isNodeMaterial) m.opacity = src.opacity * v;
    }
    refresh();
  }
  const same = (a, b) => a && b && a.level === b.level && a.key === b.key;
  const piecesOf = (s) => !X || !s ? [] : s.level === "part" ? X.tops[s.key].pieces : [s.key];
  function boxOfPieces(pcs) {
    const set = new Set(pcs), b = new THREE.Box3();
    if (X) for (const m of X.subs) if (set.has(m.userData.avPiece)) { m.updateWorldMatrix(true, false); if (!m.geometry.boundingBox) m.geometry.computeBoundingBox(); b.union(m.geometry.boundingBox.clone().applyMatrix4(m.matrixWorld)); }
    return b;
  }
  function flyTo(pcs) {
    if (!X || !pcs.length) return;
    const b = boxOfPieces(pcs);
    if (b.isEmpty()) return;
    const c = b.getCenter(new THREE.Vector3()), d = Math.max(...b.getSize(new THREE.Vector3()).toArray()) * 1.6 + 1;
    const dir = camera.position.clone().sub(nav.target ?? c).normalize();
    if (!(dir.lengthSq() > .5)) dir.set(.6, .45, .6).normalize();
    nav.fly(nav.poseOf(c.clone().addScaledVector(dir, d), c));
  }

  // ---- pointing -----------------------------------------------------------------------------------------------------
  // the nearest hit that is SHOWN: not cut away, not hidden, not a fully faded layer, not a cap or a highlight
  const rc = new THREE.Raycaster();
  const clippedAway = (p) => planes.some((q) => q.distanceToPoint(p) < -1e-4);
  function hit(ray, list = roots()) {
    const hits = ray.intersectObjects(list.filter(Boolean), true);
    for (const h of hits) {
      const o = h.object;
      if (!o.isMesh || o.userData.av) continue;
      let seen = true;
      for (let q = o; q; q = q.parent) if (!q.visible) { seen = false; break; }
      if (!seen || clippedAway(h.point)) continue;
      if (o.userData.avLayer !== undefined && layerVal[o.userData.avLayer] < .05) continue;
      return h;
    }
    return null;
  }
  // a CLICK (not a drag) on the building picks the part under it
  let downAt = null;
  canvas.addEventListener("pointerdown", (e) => { downAt = e.button === 0 ? [e.clientX, e.clientY, performance.now()] : null; });
  canvas.addEventListener("pointerup", (e) => {
    if (!downAt || !B || !open.parts) return;
    const [x, y, t] = downAt; downAt = null;
    if (Math.hypot(e.clientX - x, e.clientY - y) > 4 || performance.now() - t > 500) return;
    explode();
    const r = canvas.getBoundingClientRect();
    rc.setFromCamera(new THREE.Vector2((e.clientX - r.left) / r.width * 2 - 1, 1 - (e.clientY - r.top) / r.height * 2), camera);
    const h = hit(rc, X ? [X.group, B.doors] : roots());
    const pi = h?.object.userData.avPiece;
    selected = pi === undefined || pi < 0 ? null : { level, key: level === "part" ? X.pieces[pi].topIndex : pi };
    refresh();
  });
  addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || e.target.tagName === "TEXTAREA" || e.target.tagName === "INPUT") return;
    if (isolated) isolated = null; else selected = null;
    refresh();
  });

  // ---- the asset on the stand ---------------------------------------------------------------------------------------
  // what is on the stand, after every build: { path, root } for any 3D asset (cuts only), and with { doors, asm, def }
  // for a building (its doors' group, its assembly, its definition as built); null: nothing 3D (a 2D sheet)
  function attach(o) {
    const again = !!o && o.path === path;
    // (the same asset rebuilt -- its definition being typed: the cuts stay where they are, and what was hidden, picked
    //  and isolated is kept, by name)
    keep = again && X ? { hidden: [...hidden].map((i) => X.pieces[i]?.name).filter(Boolean),
                          selected: selected && { level: selected.level, name: (selected.level === "part" ? X.tops : X.pieces)[selected.key]?.name },
                          isolated: isolated && { level: isolated.level, name: (isolated.level === "part" ? X.tops : X.pieces)[isolated.key]?.name } } : null;
    B = o?.asm ? o : null; target = o && !o.asm ? o.root : null; X = null; hidden.clear(); selected = isolated = null;
    const nb = o ? boxOf?.() ?? new THREE.Box3() : new THREE.Box3();
    if (!nb.isEmpty()) box = nb.clone();
    if (!again) {   // (another asset: no cuts, every layer whole)
      path = o?.path ?? null;
      for (const c of cuts) { c.on = false; c.flip = false; c.at = mid(c.i); }
      for (let i = 0; i < LAYERS.length; i++) { layerVal[i] = 1; layerU[i].value = 1; }
    }
    panel.style.display = o ? "flex" : "none";
    if (B && (open.parts || open.layers || layerVal.some((v) => v < 1) || keep)) explode();
    update();
  }
  update();
  panel.style.display = "none";
  return {
    attach, hit, explode, get exploded() { return X; },
    get state() { return { box: [box.min.toArray(), box.max.toArray()].map((v) => v.map((q) => +q.toFixed(2))), cuts: cuts.map((c) => ({ ...c })), layers: [...layerVal], selected: selected && X ? (selected.level === "part" ? X.tops[selected.key].name : X.pieces[selected.key].name) : null,
                           isolated: !!isolated, hidden: hidden.size, exploded: X ? { meshes: X.subs.length, parts: X.tops.length, ms: Math.round(X.ms), unmatched: X.unmatched, layerTris: X.layerTris } : null }; },
    // (for a driver: the cuts and layers set without the pointer)
    cut(i, on, at01 = .5, flip = false) { const c = cuts[i]; c.on = on; c.flip = flip; c.at = box.min.getComponent(i) + (box.max.getComponent(i) - box.min.getComponent(i)) * at01; update(); },
    faceCut, setLayer, open(k, on = true) { open[k] = on; if (on && k !== "cuts") explode(); paint(); },
    select(name, lv = "part") { if (!X) explode(); if (!X) return false; level = lv; const arr = lv === "part" ? X.tops : X.pieces, k = arr.findIndex((q) => q.name === name); selected = k >= 0 ? { level: lv, key: k } : null; refresh(); return k >= 0; },
    selectedBox() { return selected ? boxOfPieces(piecesOf(selected)) : null; },
    isolate() { bIso.onclick(); }, hide() { bHide.onclick(); }, showAll() { bAll.onclick(); }, frame() { bFrame.onclick(); },
  };
}

// a triangle's layer, by its part's kind, the way it faces (n), and which side of it is in -- told as arch/finish.js
// tells it (finishPieces sideOf): a dome's face turned toward its own axis is its inside, a roof's upper face and a
// dome's skin the open air's, a vault's face turned down its ceiling, the rest by the building's interiors (the air
// 30 cm before the face in one of them). c: its middle; o: its placing's origin [x, z]
function classify(p, n, c, o, vols) {
  const k = p.kind;
  const side = () => {
    if (k === "dome" || k === "vault") {
      const toward = n.x * (c.x - o[0]) + n.z * (c.z - o[1]);
      if (n.y < (k === "dome" ? .9 : .3) && (toward < 0 || n.y < -.9)) return "in";
      if (k === "dome") return "out";
    }
    if (k === "roof" && n.y > .2) return "out";
    if ((k === "groin" || k === "ribs" || k === "vault") && n.y < -.5) return "in";
    return vols.length && inInterior(vols, c.x + n.x * .3, c.y + n.y * .3, c.z + n.z * .3) ? "in" : "out";
  };
  const wall = () => side() === "in" ? "inner" : "outer";
  if (k === "glass" || k === "tracery") return "windows";
  if (STAIRS.has(k) || p.stairPart) return "stairs";
  if (ORNAMENT.has(k)) return "ornament";
  if (ROOFS.has(k)) return n.y <= -.2 ? "ceilings" : k === "roof" && Math.abs(n.y) < .05 ? wall() : side() === "out" ? "roofs" : "ceilings";   // (a gable end: a wall)
  if (VAULTS.has(k)) return n.y > .2 && side() === "out" ? "roofs" : "ceilings";
  if (n.y >= .7) return k === "wall" || k === "column" ? wall() : "floors";
  if (n.y <= -.7) return "ceilings";
  return wall();
}

// THE ASSEMBLY'S OWN TRIANGLES, placed, in a grid: which of them a drawn triangle was cut out of (in its plane, its
// middle inside it), and which lies nearest a point
function triangleIndex(asm) {
  let T = 0;
  for (const p of asm.parts) if (p.kind !== "item" && p.kind !== "marker" && p.geometry?.index) T += p.geometry.index.length / 3 * p.instances.length;
  const D = new Float64Array(T * 13), part = new Int32Array(T), org = new Float32Array(T * 2);
  let t = 0;
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  asm.parts.forEach((p, pi) => {
    if (p.kind === "item" || p.kind === "marker" || !p.geometry?.index) return;
    const P = p.geometry.position, I = p.geometry.index;
    for (const [yaw, X, Y, Z] of p.instances) {
      const c = Math.cos(yaw), s = Math.sin(yaw);
      for (let k = 0; k < I.length; k += 3) {
        const o = t * 13, v = [];
        for (let e = 0; e < 3; e++) { const j = I[k + e]; v.push(P[j * 3] * c + P[j * 3 + 2] * s + X, P[j * 3 + 1] + Y, -P[j * 3] * s + P[j * 3 + 2] * c + Z); }
        const ux = v[3] - v[0], uy = v[4] - v[1], uz = v[5] - v[2], wx = v[6] - v[0], wy = v[7] - v[1], wz = v[8] - v[2];
        let nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx; const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l;
        D[o] = v[0]; D[o + 1] = v[1]; D[o + 2] = v[2]; D[o + 3] = ux; D[o + 4] = uy; D[o + 5] = uz; D[o + 6] = wx; D[o + 7] = wy; D[o + 8] = wz;
        D[o + 9] = nx; D[o + 10] = ny; D[o + 11] = nz; D[o + 12] = nx * v[0] + ny * v[1] + nz * v[2];
        part[t] = pi; org[t * 2] = X; org[t * 2 + 1] = Z;
        for (let q = 0; q < 9; q++) { const a = q % 3; if (v[q] < lo[a]) lo[a] = v[q]; if (v[q] > hi[a]) hi[a] = v[q]; }
        t++;
      }
    }
  });
  const diag = Math.hypot(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) || 1, h = Math.min(4, Math.max(.4, diag / 160));
  const cells = new Map(), big = [];
  const key = (i, j, k) => (i * 73856093) ^ (j * 19349663) ^ (k * 83492791);
  for (let q = 0; q < T; q++) {
    const o = q * 13;
    let x0 = D[o], x1 = D[o], y0 = D[o + 1], y1 = D[o + 1], z0 = D[o + 2], z1 = D[o + 2];
    for (const [dx, dy, dz] of [[D[o + 3], D[o + 4], D[o + 5]], [D[o + 6], D[o + 7], D[o + 8]]]) {
      const x = D[o] + dx, y = D[o + 1] + dy, z = D[o + 2] + dz;
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; if (z < z0) z0 = z; if (z > z1) z1 = z;
    }
    const i0 = Math.floor((x0 - .01) / h), i1 = Math.floor((x1 + .01) / h), j0 = Math.floor((y0 - .01) / h), j1 = Math.floor((y1 + .01) / h), k0 = Math.floor((z0 - .01) / h), k1 = Math.floor((z1 + .01) / h);
    if ((i1 - i0 + 1) * (j1 - j0 + 1) * (k1 - k0 + 1) > 400) { big.push(q); continue; }
    for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) for (let k = k0; k <= k1; k++) {
      const kk = key(i, j, k); let L = cells.get(kk); if (!L) cells.set(kk, L = []); L.push(q);
    }
  }
  const at = (p, f) => { const L = cells.get(key(Math.floor(p.x / h), Math.floor(p.y / h), Math.floor(p.z / h))); if (L) for (const q of L) f(q); for (const q of big) f(q); };
  const normalOf = new THREE.Vector3();
  // how far outside triangle q the point is (0 inside), in its plane
  const outside = (q, px, py, pz) => {
    const o = q * 13, vx = px - D[o], vy = py - D[o + 1], vz = pz - D[o + 2];
    const d00 = D[o + 3] ** 2 + D[o + 4] ** 2 + D[o + 5] ** 2, d01 = D[o + 3] * D[o + 6] + D[o + 4] * D[o + 7] + D[o + 5] * D[o + 8], d11 = D[o + 6] ** 2 + D[o + 7] ** 2 + D[o + 8] ** 2;
    const d20 = vx * D[o + 3] + vy * D[o + 4] + vz * D[o + 5], d21 = vx * D[o + 6] + vy * D[o + 7] + vz * D[o + 8], den = d00 * d11 - d01 * d01;
    if (!(Math.abs(den) > 1e-18)) return Infinity;
    const u = (d11 * d20 - d01 * d21) / den, w = (d00 * d21 - d01 * d20) / den;
    return Math.max(0, -u, -w, u + w - 1) * Math.sqrt(Math.max(d00, d11));
  };
  const self = {
    normalOf, origin: [0, 0],   // (the last found: its triangle's normal, its placing's origin)
    // the part a drawn triangle (its middle c, its normal n) was cut from: in the plane of one, its middle inside it
    find(c, n) {
      let best = -1, score = Infinity;
      at(c, (q) => {
        const o = q * 13, dist = Math.abs(D[o + 9] * c.x + D[o + 10] * c.y + D[o + 11] * c.z - D[o + 12]);
        if (dist > .05) return;
        const al = Math.abs(D[o + 9] * n.x + D[o + 10] * n.y + D[o + 11] * n.z);
        const s = dist + outside(q, c.x, c.y, c.z) + (al < .98 ? .02 : 0);
        if (s < score) { score = s; best = q; }
      });
      if (best < 0 || score > .08) { normalOf.copy(n); return -1; }
      const o = best * 13; normalOf.set(D[o + 9], D[o + 10], D[o + 11]); self.origin[0] = org[best * 2]; self.origin[1] = org[best * 2 + 1];
      return part[best];
    },
    // the part whose stone lies nearest a point (a door leaf's middle: the reveals of its doorway), within a couple of metres
    near(c) {
      let best = -1, bd = Infinity;
      const p = new THREE.Vector3();
      for (const dx of [-h, 0, h]) for (const dy of [-h, 0, h]) for (const dz of [-h, 0, h]) {
        p.set(c.x + dx, c.y + dy, c.z + dz);
        at(p, (q) => {
          const o = q * 13, dist = Math.abs(D[o + 9] * c.x + D[o + 10] * c.y + D[o + 11] * c.z - D[o + 12]) + outside(q, c.x, c.y, c.z);
          if (dist < bd) { bd = dist; best = q; }
        });
      }
      return best >= 0 && bd < 3 ? part[best] : -1;
    },
  };
  return self;
}
