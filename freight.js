// The freight chain: goods and what each of their states means, the
// barge that brings them, the landing's dock hands who unload it, the
// freight carts' stops (load at the quay, unload in a yard), and pieces set
// down on moving floors. index.html hands over the world it needs
// (createFreight(world)) and keeps only the player's side (what you carry).
//
// Goods are a pool of barrels and sacks, two instanced meshes; each item
// is somewhere: in the barge's hold, in a hand's arms, on the quay, on a
// cart's bed, in a yard (where it is consumed after a while and returns
// to the pool), on the ground where you dropped it, or in your arms.
//
// THE VESSELS FOLLOW THE CULTURE (2026-11-03): what the goods travel in is DATA, assets/world/goods.json -- per
// culture (the period, else its dress) the freight's vessels by weight, how a porter carries each, the road carts'
// loads, a store's jars. A Greek town ships amphorae (lying in straw, carried on the shoulder) and keeps pithoi; an
// Egyptian one jars and baskets on the head; a Chinese one tubs on a carrying pole; a medieval one casks, sacks and
// crates. Each vessel kind is its own instanced set; `rest` lays a piece down its own way (an amphora on its belly, a
// sack across), and the dock hands have a rig for each carrying pose their culture's vessels need (people.js poses
// carry, shoulder, head, pole, back, tumpline), with the pole or the strap carried along as an item.
import * as THREE from "three";
import { itemGroup, itemInstanced } from "./architecture.js";   // (the casks, sacks, barge and gangplank are items: assets/items)
import { ASSETS } from "./catalogue.js";

const GOODS_DEF = () => ASSETS.get("world/goods") ?? { vessels: {}, carry: {}, cultures: {} };
// the culture's goods table: by the period's name, else by the first of its dress styles that has one, else `default`
export function goodsCulture(period, dress) {
  const C = GOODS_DEF().cultures ?? {};
  const key = C[period] ? period : Object.keys(dress ?? {}).find((k) => C[k]) ?? "default";
  return { key, ...(C[key] ?? C.default ?? { freight: { cask: 1, sack: 1 }, loads: [0, 1, 2, 3, 4] }) };
}
const DEG = Math.PI / 180;
const frameOf = (o, m = new THREE.Matrix4()) => o ? m.compose(new THREE.Vector3(...(o.at ?? [0, 0, 0])),
  new THREE.Quaternion().setFromEuler(new THREE.Euler(...(o.rot ?? [0, 0, 0]).map((d) => d * DEG))), new THREE.Vector3(1, 1, 1)) : m.identity();

// world: { scene, BUILDINGS, LANDING, BASIN, freightLane, bargeDef, createComposite, makePerson, gaitBase,
//          talkers, track, movers, cartUnder, carts, riverZ, riverHW, VILLAGE_X, WLEVEL, waterAt(x, z) (the surface there: a
//          grown map's river falls downstream), handHerds }
export function createFreight(world) {
  const { scene, BUILDINGS, LANDING, BASIN, freightLane, bargeDef, createComposite, makePerson, gaitBase,
          talkers, track, movers, cartUnder, carts, riverZ, riverHW, VILLAGE_X, WLEVEL, waterAt = () => WLEVEL, handHerds,
          culture = goodsCulture(null, null) } = world;
  const goods = [], goodsSets = {}, G = GOODS_DEF();
  const vessel = (it) => G.vessels?.[it.kind] ?? {};
  const restM = {}, carriedM = {};   // per kind: how it lies set down; per kind and style: where it sits when carried
  const styleOf = (it) => culture.carry?.[it.kind] ?? vessel(it).carry ?? "arms";
  // ONE table of what each state of a piece means. Everything that asks --
  // can it be picked up, does it hold a quay slot, what to release when it
  // moves on -- reads this table, and goodsTo() is the only way to change a
  // state (so leaving the barge's hold or a cart's load is always tidied up).
  //   pick: you can pick it up here   quaySlot: it holds (or has reserved) its quay slot   leave: tidy-up on leaving
  const GOODS = {
    gone:    {},                                                            // back in the pool, out of sight
    hold:    { pick: true, leave: (it) => { const h = it.ship?.hold ?? bargeSt.hold; h.splice(h.indexOf(it), 1); it.ship = null; } },   // in the barge's hold, or a moored ship's (it.ship: harbour.js)
    carried: { quaySlot: true },                                            // in a dock hand's arms, its quay slot reserved
    quay:    { pick: true, quaySlot: true },                                // on a quay slot, waiting for a cart
    cart:    { pick: true, leave: (it) => { for (const k of carts) { const i = k.items.indexOf(it); if (i >= 0) k.items.splice(i, 1); } } },   // on a freight cart's bed
    store:   { pick: true },                                                // in a yard, consumed after a while
    ground:  { pick: true },                                                // where someone put it down
    riding:  { pick: true, leave: (it) => { it.mover = null; } },           // set down on a moving floor, riding it
    player:  {},                                                            // in your arms
  };
  function goodsTo(it, state) {
    if (!GOODS[state]) throw new Error(`goods: no state "${state}"`);
    if (it.state !== state) GOODS[it.state]?.leave?.(it);
    it.state = state;
    return it;
  }
  // (every placement comes here; the item keeps a copy of where it is -- an arrow stuck in it follows it: archery.js)
  const placeItemM = (it, m) => { goodsSets[it.kind].set(it.idx, m); (it.m ??= new THREE.Matrix4()).copy(m); };
  // set down (on the quay, a bed, a yard, the ground, in the hold): `m` the spot and its heading, the piece laid its way
  const placeRest = (it, m) => placeItemM(it, _im2.multiplyMatrices(m, restM[it.kind] ?? _id));
  const _im = new THREE.Matrix4(), _im2 = new THREE.Matrix4(), _id = new THREE.Matrix4();
  const placeItem = (it, x, y, z, rotY = 0) => { _im.makeRotationY(rotY).setPosition(x, y, z); placeRest(it, _im); it.x = x; it.y = y; it.z = z; };
  // carried: (x, y, z) the carrying style's anchor, rotY the carrier's heading -- the piece where that style holds it
  // (the arms': a cask as it stands, a sack stood up on end; the shoulder's: an amphora along it, toe behind)
  const placeCarried = (it, x, y, z, rotY, style = "arms") => {
    _im.makeRotationY(rotY).setPosition(x, y, z);
    placeItemM(it, _im2.multiplyMatrices(_im, carriedM[it.kind]?.[style] ?? _id)); it.x = x; it.y = y; it.z = z;
  };
  const hideItem = (it) => placeItem(it, 0, -100, 0);
  // Put a piece down where you stand. On a moving floor -- the barge's deck, a
  // cart's bed, the lowered plank -- it RIDES: its place and heading are kept
  // in that floor's own frame and it is placed from the floor's transform
  // every frame (placeRiding), so it sails or rolls away with it.
  const _ri = new THREE.Matrix4(), _rv = new THREE.Vector3();
  const yawOfM = (m) => Math.atan2(-m.elements[2], m.elements[0]);
  function putDown(it, x, y, z, yaw) {
    const k = cartUnder(x, z, y);
    if (k && !k.ramp) {   // (not on a ship's plank: a piece set down at its foot stays on the quay)
      k.body.updateMatrixWorld();
      goodsTo(it, "riding"); it.mover = k;
      it.local = new THREE.Vector3(x, y + .01, z).applyMatrix4(_ri.copy(k.body.matrixWorld).invert());
      it.lyaw = yaw - yawOfM(k.body.matrixWorld);
      placeRiding();
    } else { goodsTo(it, "ground"); placeItem(it, x, y + .01, z, yaw); }
  }
  function placeRiding() {
    for (const it of goods) {
      if (it.state !== "riding") continue;
      const b = it.mover.body;
      b.updateMatrixWorld();
      _rv.copy(it.local).applyMatrix4(b.matrixWorld);
      placeItem(it, _rv.x, _rv.y, _rv.z, yawOfM(b.matrixWorld) + it.lyaw);
    }
  }
  let bargeSt = null, bargeGrp = null, LANDER = null;   // the barge's state and mesh; the landing's world helpers
  const hands = [];
  let styles = [];   // (the carrying styles the culture's vessels need: one loaded rig per style and hand -- goods.json `carry`)
  // a DOCK HAND, banner people in the folk herd's way, in `herd`: a rig walking free, and one walking loaded for each way
  // of carrying; `post` where they wait; `extra` theirs (a port's hand: its `dock`, harbour.js)
  function makeHand(herd, seed, post, extra = {}) {
    const pd = makePerson({ seed, adult: true, work: true }), an = herd.add(pd), rigs = {};
    for (const s of styles) { rigs[s] = herd.add(makePerson({ seed, pose: G.carry[s].pose, adult: true, work: true })); rigs[s].position.set(0, -100, 0); rigs[s].animT = 0; }
    const anC = rigs[styles[0]] ?? an;
    const h = { an, anC, rigs, eyeY: pd.eyeAt?.[1] ?? 1.6, withs: {}, base: gaitBase(pd), state: "idle", item: null, wp: [], wi: 0, speed: 1.4, seed, post, ...extra };
    an.position.set(post[0], post[1] + .04, post[2]); an.animT = 0;
    hands.push(h); talkers.push({ p: an, seed: h.seed, kind: pd.kind, figure: () => (h.anC.down ? h.anC : an) });   // (figure: the one shown -- struck down, it is silent)
    track(() => [an.position.x, an.position.y, an.position.z, an.rotY, an.animT], (v) => { an.position.set(v[0], v[1], v[2]); an.rotY = v[3]; an.animT = v[4]; }, { angles: [3], live: () => !an.down });
    return h;
  }
  if ((LANDING && freightLane) || world.port) {   // (world.port: a world with a sea port has the pool even with no landing)
    // the pool: `pool` pieces shared out among the culture's vessels by weight (goods.json), each kind its own instanced set
    // (a port's ships' holds want more of them: harbour.js)
    const kinds = Object.entries(culture.freight ?? { cask: 1, sack: 1 }).filter(([k]) => G.vessels?.[k]), W = kinds.reduce((a, [, w]) => a + w, 0);
    const counts = kinds.map(([k, w]) => [k, Math.max(2, Math.round(((G.pool ?? 28) + (world.port ? 26 : 0)) * w / W))]);
    for (const [k, n] of counts) {
      const V = G.vessels[k];
      goodsSets[k] = itemInstanced(V.item, n, { params: V.params ?? {} });   // (each stood on its foot at the origin; `rest` lays it down)
      scene.add(goodsSets[k].root);
      restM[k] = frameOf(V.rest);
      carriedM[k] = Object.fromEntries(Object.entries(V.carried ?? {}).map(([s, o]) => [s, frameOf(o)]));
      const b = goodsSets[k].built.bounds, box = b ? [b.lo, b.hi] : null;
      for (let i = 0; i < n; i++) goods.push({ kind: k, name: V.name ?? k, idx: i, state: "gone", cyl: V.item === "items/furniture/cask", box });
    }
    // (handed out in turn, kind after kind: the barge's first load is mixed)
    goods.sort((a, b) => a.idx - b.idx || counts.findIndex(([k]) => k === a.kind) - counts.findIndex(([k]) => k === b.kind));
    for (const it of goods) hideItem(it);
    styles = [...new Set(counts.map(([k]) => styleOf({ kind: k })))].filter((s) => G.carry?.[s]);
  }
  if (LANDING && freightLane) {
    const def = BUILDINGS.landing, L = LANDING;
    LANDER = { x: L.x, z: L.z, slots: def.quaySlots.map(([x, y, z]) => [L.x + x, y, L.z + z]),
               way: def.way.map(([x, y, z]) => [L.x + x, y, L.z + z]), bargeZ: L.z + def.bargeZ };
    // the barge: sails in from 120m downriver, moors at the landing, is unloaded, sails out, waits, comes back laden
    const bd = bargeDef();
    bargeGrp = itemGroup(bd.item); scene.add(bargeGrp);
    bargeSt = { x: BASIN.x - 40, moorX: BASIN.x, outX: BASIN.x - 120, speed: 1.6, phase: "in", t: 0, def: bd, hold: [],
                body: bargeGrp, yaw: 0, carry: { dx: 0, dz: 0, dyaw: 0 }, halfL: bd.halfL, halfW: bd.halfW, top: bd.deckY, side: .35, moving: true };
    movers.push(bargeSt);
    const refill = () => { const pool = goods.filter((g) => g.state === "gone"); for (let i = 0; i < bd.holdSlots.length && pool.length; i++) { const it = pool[i % 2 ? 0 : pool.length - 1]; pool.splice(pool.indexOf(it), 1); goodsTo(it, "hold"); it.slot = i; bargeSt.hold.push(it); } };
    refill();
    // two dock hands: their own little herd
    const handHerd = createComposite((2 * (1 + styles.length) + 1) * 60); scene.add(handHerd.mesh);   // two hands x their rigs, and the boatman
    for (let i = 0; i < 2; i++) {   // (each hand's own waiting post on the quay)
      const start = LANDER.way[3];
      makeHand(handHerd, 900 + i * 3, [start[0] + 1.5 + i * 1.6, .05, start[2] - 2.2]);
    }
    {   // the boatman: stands at the tiller behind the cabin, rides with the barge, talks
      const pb = makePerson({ seed: 907, still: true, adult: true }), an = handHerd.add(pb);
      an.animT = 0; bargeSt.boatman = an; talkers.push({ p: an, seed: 907, kind: pb.kind });
    }
    // the gangplank: hinged at the barge's north gunwale; a moving floor of its own when lowered
    {
      const pg = itemGroup("items/components/gangplank");
      pg.position.set(-.5, bd.deckY, -1.72); pg.rotation.x = -1.35;   // raised, folded up along the gunwale
      bargeGrp.add(pg);
      bargeSt.plank = pg;
      bargeSt.plankMover = { body: { position: new THREE.Vector3() }, yaw: 0, carry: bargeSt.carry, halfL: .6, halfW: 1.35, top: bd.deckY + .03, active: false };
    }
    handHerds.push(handHerd);
  }
  // the barge's pose along the north side of the river, 8.5m out from the bank line
  const bargePose = (x) => {
    // the lane runs 8.5m off the north bank, but for 30m either side of the bridge it eases onto the river's
    // center line and straightens: the barge passes through the middle arch square, clear of both piers
    const zc = (xx) => {
      const zl = riverZ(xx) - riverHW(xx) + 8.5;
      if (VILLAGE_X === null) return zl;
      const d = Math.abs(xx - VILLAGE_X); if (d >= 30) return zl;
      const t = d / 30, w = t * t * (3 - 2 * t);
      return riverZ(VILLAGE_X) * (1 - w) + zl * w;
    };
    return { x, z: zc(x), yaw: Math.atan2(-(zc(x + .5) - zc(x - .5)), 1) };
  };
  const bargeLocal = ([lx, ly, lz]) => {   // a barge-local point in world space, from the SIM pose (the mesh lags a frame)
    const p = bargePose(bargeSt.x), c = Math.cos(p.yaw), sn = Math.sin(p.yaw);
    return [p.x + lx * c + lz * sn, waterAt(p.x, p.z) + ly, p.z - lx * sn + lz * c];
  };
  const bargeHoldWorld = (it) => bargeLocal(bargeSt.def.holdSlots[it.slot]);
  function placeBarge(frac) {
    if (!bargeSt) return;
    const xv = bargeSt.x + (bargeSt.phase === "in" ? bargeSt.speed * frac : bargeSt.phase === "out" ? -bargeSt.speed * frac : 0);
    const p = bargePose(xv);
    bargeSt.carry.dx += p.x - bargeGrp.position.x; bargeSt.carry.dz += p.z - bargeGrp.position.z;
    bargeSt.carry.dyaw += ((p.yaw - bargeSt.yaw + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
    bargeSt.yaw = p.yaw;
    bargeGrp.position.set(p.x, waterAt(p.x, p.z), p.z); bargeGrp.rotation.y = p.yaw;
    if (bargeSt.boatman) {   // (struck down, combat.js: he lies on the deck and rides on with it -- only his height and turn are his fall's)
      const w = bargeLocal([-5.3, bargeSt.def.deckY + .04, 0]), bm = bargeSt.boatman;
      bm.position.x = w[0]; bm.position.z = w[2];
      if (!bm.down) { bm.position.y = w[1]; bm.rotY = p.yaw; }
    }
    if (bargeSt.plank) {   // lower the plank when moored, raise it under way; as a floor it exists only when down
      const want = bargeSt.phase === "moored" ? 0 : -1.35;
      bargeSt.plank.rotation.x += (want - bargeSt.plank.rotation.x) * Math.min(1, frac * 0 + .08);
      const pm = bargeSt.plankMover, down = bargeSt.plank.rotation.x > -.08;
      if (down && !pm.active) { movers.push(pm); pm.active = true; }
      if (!down && pm.active) { movers.splice(movers.indexOf(pm), 1); pm.active = false; }
      const w = bargeLocal([-.5, 0, -3.05]); pm.body.position.set(w[0], waterAt(p.x, p.z), w[2]); pm.yaw = p.yaw;
    }
    const c = Math.cos(p.yaw), sn = Math.sin(p.yaw);
    for (const it of bargeSt.hold) { const s = bargeSt.def.holdSlots[it.slot]; placeItem(it, p.x + s[0] * c + s[2] * sn, waterAt(p.x, p.z) + s[1], p.z - s[0] * sn + s[2] * c, p.yaw); }   // (laid each its way: `rest`)
  }
  // the hands' way: the barge's plank end (moored), then the landing's waypoints, then a quay slot
  const bargePlankWorld = () => bargeLocal(bargeSt.def.plankEnd);
  const freeQuaySlot = () => LANDER.slots.findIndex((_, i) => !goods.some((g) => GOODS[g.state].quaySlot && g.slot === i));   // carried pieces hold their slot
  function freightStep(dt) {
    if (!bargeSt && !docks.length) return;
    const B = bargeSt;
    if (B) {
    B.t += dt;
    if (B.phase === "in") { B.x += B.speed * dt; if (B.x >= B.moorX) { B.x = B.moorX; B.phase = "moored"; B.t = 0; } }
    else if (B.phase === "moored") { if (!B.hold.length && !hands.some((h) => h.item && !h.dock) && B.t > 12) { B.phase = "out"; B.t = 0; } }
    else if (B.phase === "out") { B.x -= B.speed * dt; if (B.x <= B.outX) { B.phase = "away"; B.t = 0; } }
    else if (B.phase === "away" && B.t > 25) { const pool = goods.filter((g) => g.state === "gone"); for (let i = 0; i < B.def.holdSlots.length && pool.length; i++) { const it = pool.shift(); goodsTo(it, "hold"); it.slot = i; B.hold.push(it); } B.phase = "in"; B.t = 0; }
    B.moving = B.phase === "in" || B.phase === "out";
    }
    // the hands
    for (const h of hands) {
      const p = h.an.position;
      if (h.an.down || h.anC.down) {   // struck down (combat.js): the load dropped where they fell, the item they were after given up
        if (!h.fallen) {
          h.fallen = true;
          if (h.target) { delete h.target.claimed; h.target = null; }
          if (h.item) { const it = h.item, q = (h.anC.down ? h.anC : h.an).position; h.item = null; goodsTo(it, "ground"); placeItem(it, q.x + .6, q.y, q.z, 0); }
        }
        continue;
      }
      h.an.ampT = h.anC.ampT = h.state === "idle" ? 0 : 1;   // the stride settles while they wait
      if (h.state === "idle") {
        h.an.animT += (Math.round(h.an.animT * 1.6) / 1.6 - h.an.animT) * Math.min(1, dt * 10);
        if (h.dock) dockIdle(h);   // (a port's hand: a moored ship's hold, below)
        else if (B.phase === "moored" && B.hold.some((it) => !it.claimed)) {
          const it = B.hold.find((it) => !it.claimed); it.claimed = true; h.target = it;
          h.wp = [...LANDER.way.slice().reverse(), bargePlankWorld(), bargeHoldWorld(it)]; h.wi = 0; h.state = "toHold";
        }
        continue;
      }
      const wp = h.wp[h.wi], dx = wp[0] - p.x, dz = wp[2] - p.z, d = Math.hypot(dx, dz);
      const step = h.speed * dt;
      if (d <= step) {
        p.set(wp[0], wp[1] + .04, wp[2]);
        if (++h.wi >= h.wp.length) {
          if (h.dock) dockArrive(h);
          else if (h.state === "toHold") {   // pick the item up, carry it to a free quay slot
            const it = h.target; goodsTo(it, "carried"); h.item = it; h.target = null;   // (leaving the hold takes it off the manifest)
            h.style = styleOf(it); h.anC = h.rigs[h.style] ?? h.anC;   // (the rig that carries it its culture's way)
            const si = freeQuaySlot(); h.slotI = si < 0 ? 0 : si; it.slot = h.slotI;   // reserved now
            h.wp = [bargePlankWorld(), ...LANDER.way, LANDER.slots[h.slotI]]; h.wi = 0; h.state = "toQuay"; h.speed = 1.1;
          } else if (h.state === "toQuay") {   // set it down, then step back to the waiting post
            const it = h.item, sl = LANDER.slots[h.slotI]; goodsTo(it, "quay"); it.slot = h.slotI; delete it.claimed;
            placeItem(it, sl[0], sl[1], sl[2], 0); h.item = null; h.speed = 1.5;
            h.state = "toPost"; h.wp = [h.post]; h.wi = 0;
          } else { h.state = "idle"; h.wp = []; }   // at the post
        }
      } else {
        p.x += dx / d * step; p.z += dz / d * step;
        const t = step / d; p.y += (wp[1] + .04 - p.y) * Math.min(1, t * 1.0 + .02);
        h.an.rotY = Math.atan2(-dz, dx);
        h.an.animT += dt * h.speed / h.base;
      }
    }
    // yards consume: a delivered item is gone after 90s (and the barge will bring it back)
    for (const it of goods) if (it.state === "store") { it.age = (it.age ?? 0) + dt; if (it.age > 90) { goodsTo(it, "gone"); it.age = 0; hideItem(it); } }
  }
  // A SEA PORT'S DOCK (harbour.js): D { ships (each: moored, hold [], holdWorld(it), plankTop(), plankFoot(), way()),
  // stores ({ door, slots } each: a warehouse's stack in front of its door), posts (where the hands wait) }. Its own hands
  // carry a moored ship's hold up the plank, over the apron and in to a warehouse's stack; the stack is consumed as a
  // yard's is (90 s) and the pool loads the next ship that moors (loadShip).
  const docks = [];
  function addDock(D) {
    const herd = createComposite(D.posts.length * (1 + styles.length) * 60); scene.add(herd.mesh); handHerds.push(herd);
    D.posts.forEach((post, i) => makeHand(herd, 950 + i * 5, post, { dock: D }));
    docks.push(D);
    return { busy: (S) => hands.some((h) => h.ship === S && !h.fallen && (h.state === "toHold" || (h.state === "toStore" && h.wi < 2))) };
  }
  function loadShip(S, n) {   // a ship that moors comes laden: up to n pieces from the pool into its hold
    const pool = goods.filter((g) => g.state === "gone");
    for (let i = 0; i < n && pool.length; i++) { const it = pool.splice(i % 2 ? 0 : pool.length - 1, 1)[0]; goodsTo(it, "hold"); it.ship = S; it.slot = i; S.hold.push(it); }
  }
  const storeFree = (W) => W.slots.findIndex((_, i) => !goods.some((g) => (g.state === "store" && g.yard === W && g.slot === i) || (g.state === "carried" && g.wyard === W && g.wslot === i)));
  function dockIdle(h) {   // the nearest moored ship with something in its hold still unclaimed, while a stack has room
    const D = h.dock, p = h.an.position;
    if (!D.stores.some((W) => storeFree(W) >= 0)) return;
    let best = null, bd = Infinity;
    for (const S of D.ships) {
      if (S.state !== "moored" || !S.plankSide || !S.hold.some((it) => !it.claimed)) continue;
      const d = Math.hypot(S.x - p.x, S.z - p.z); if (d < bd) { bd = d; best = S; }
    }
    if (!best) return;
    const it = best.hold.find((it) => !it.claimed); it.claimed = true; h.target = it; h.ship = best;
    const land = path(D, [[p.x, p.y, p.z], ...best.way(), best.plankFoot()]).slice(1);   // (D.path: round what stands on the apron)
    h.wp = [...land, best.plankTop(), best.holdWorld(it)]; h.wi = 0; h.state = "toHold";
  }
  function dockArrive(h) {
    const D = h.dock, S = h.ship;
    if (h.state === "toHold") {   // take it up; the nearest stack with room, back down the plank and over the apron to it
      const it = h.target; h.target = null;
      if (!it || it.state !== "hold" || it.ship !== S) { if (it) delete it.claimed; h.state = "toPost"; h.wp = [S.plankTop(), ...path(D, [S.plankFoot(), ...S.way().reverse(), h.post])]; h.wi = 0; return; }   // (someone else took it)
      goodsTo(it, "carried"); h.item = it; it.slot = -1;
      h.style = styleOf(it); h.anC = h.rigs[h.style] ?? h.anC;
      let W = D.stores[0], wi = -1, bd = Infinity;
      for (const V of D.stores) { const i = storeFree(V); if (i < 0) continue; const d = Math.hypot(V.door[0] - h.an.position.x, V.door[2] - h.an.position.z); if (d < bd) { bd = d; W = V; wi = i; } }
      it.wyard = W; it.wslot = Math.max(0, wi);
      h.wp = [S.plankTop(), ...path(D, [S.plankFoot(), ...S.way().reverse(), W.door, W.slots[it.wslot]])]; h.wi = 0; h.state = "toStore"; h.speed = 1.1;
    } else if (h.state === "toStore") {   // set it down on the stack, then back to the post
      const it = h.item, W = it.wyard, sl = W.slots[it.wslot];
      goodsTo(it, "store"); it.yard = W; it.slot = it.wslot; it.age = 0; delete it.claimed; it.wyard = null;
      placeItem(it, sl[0], sl[1], sl[2], W.yaw ?? 0); h.item = null; h.ship = null; h.speed = 1.5;
      h.state = "toPost"; h.wp = path(D, [sl, W.door, h.post]).slice(1); h.wi = 0;
    } else { h.state = "idle"; h.wp = []; h.ship = null; }
  }
  const path = (D, pts) => D.path?.(pts) ?? pts;
  function freightStopStep(k, dt) {   // a freight cart at its stops: load at the quay, unload at a yard
    if (k.halt) {
      k.halt.t += dt;
      const st = k.halt.stop;
      if (k.halt.t >= 3) {
        k.halt.t = 0;
        if (st.kind === "load") {
          const it = goods.find((g) => g.state === "quay");
          if (it && k.items.length < k.c.capacity) { goodsTo(it, "cart"); k.items.push(it); k.halt.idle = 0; }
          else k.halt.idle = (k.halt.idle ?? 0) + 1;
          if (k.items.length >= k.c.capacity || k.halt.idle >= 2) { k.halt = null; k.passed = st; }
        } else {
          const it = k.items.shift();
          if (it) { const y = st.yard, si = y.slots.findIndex((_, i) => !goods.some((g) => g.state === "store" && g.yard === y && g.slot === i));
            if (si >= 0) { const sl = y.slots[si]; goodsTo(it, "store"); it.yard = y; it.slot = si; it.age = 0; placeItem(it, sl[0], sl[1], sl[2], 0); }
            else { goodsTo(it, "gone"); hideItem(it); } }
          if (!k.items.length) { k.halt = null; k.passed = st; }
        }
      }
      return;
    }
    for (const st of k.stops) {
      const d = Math.abs(k.s - st.s);
      if (d > 6 && k.passed === st) k.passed = null;
      if (d < .6 && k.passed !== st) { k.halt = { stop: st, t: 0 }; k.s = st.s; break; }
    }
  }
  // THE HANDS AS DRAWN, each frame: the loaded rig of the piece's carrying style stands in for the free one while it is
  // carried, the piece where that style holds it (its anchor -- the feet, the top of the shoulder, the crown, read off
  // the figure's eyes -- turned with the carrier), and what the style carries along (the pole, the strap) with it
  const _wv = new THREE.Vector3();
  function placeHands() {
    for (const h of hands) {
      const p = h.an.position;
      const S = h.item ? G.carry?.[h.style] ?? G.carry?.arms : null;
      for (const r of Object.values(h.rigs)) if (r !== h.anC && !r.down) r.hidden = true;
      for (const [k, g] of Object.entries(h.withs)) g.visible = !!S && S.with === k && !h.an.down && !h.anC.down;
      if (h.anC.down) { h.an.hidden = true; h.anC.hidden = false; continue; }   // struck down (combat.js): the one that fell stays, where it fell
      if (h.an.down) { h.an.hidden = false; h.anC.hidden = true; continue; }
      if (!h.item) { h.an.hidden = false; h.anC.hidden = true; continue; }
      h.anC.position.copy(p); h.anC.rotY = h.an.rotY; h.anC.animT = h.an.animT; h.anC.amp = h.an.amp;
      h.an.hidden = true; h.anC.hidden = false;
      const base = S?.from === "shoulder" ? h.eyeY - .2 : S?.from === "crown" ? h.eyeY + .11 : 0, a = S?.at ?? [.42, .78, 0];
      // (the figure's frame: +x its forward, +z its right -- the world's yaw turns it as it turns the rigs)
      _wv.set(a[0], base + a[1], a[2]).applyAxisAngle(_up, h.an.rotY);
      placeCarried(h.item, p.x + _wv.x, p.y + _wv.y, p.z + _wv.z, h.an.rotY, h.style);
      if (S?.with) {
        const V = vessel(h.item), top = (goodsSets[h.item.kind].built.bounds?.hi?.[1] ?? .5);
        const g = h.withs[S.with] ??= (() => {   // (made the first time it is needed: the strap fitted to this carrier)
          const o = itemGroup(S.with, { seed: h.seed, params: S.with.endsWith("tumpline") ? { hy: h.eyeY + .05, ly: a[1] + top - .02, lx: (V.carried?.[h.style]?.at?.[0] ?? -.4) + .22 } : {} });
          o.userData.moves = true; scene.add(o); return o;
        })();
        g.visible = true;
        if (S.with.endsWith("tumpline")) g.position.set(p.x, p.y, p.z); else g.position.set(p.x + _wv.x, p.y + _wv.y, p.z + _wv.z);
        g.rotation.set(0, h.an.rotY, 0);
      }
    }
  }
  const _up = new THREE.Vector3(0, 1, 0);
  return { goods, goodsSets, GOODS, goodsTo, placeItemM, placeRest, placeCarried, putDown, placeRiding, hands, bargeSt, bargePose, placeBarge, freightStep, freightStopStep, placeHands, culture,
           addDock, loadShip, placeItem };
}
