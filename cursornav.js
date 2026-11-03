// CURSOR NAVIGATION: a camera that turns and zooms about the point UNDER THE POINTER, as the atlas's does
// (/home/martin/store/apps/atlas js/camera.js, js/main.js) -- here for three.js, y up. assets.html uses it; any lab page
// can: `const nav = createNav(camera, renderer.domElement, { pick })`, then `nav.update(dt)` each frame -- or, written for
// OrbitControls, `navControls` (below) in its place.
//
//   drag            turns the view about the point of the shown thing under the pointer: that point keeps its place
//                   in the eye's frame, so it stays where it is on the page and the thing turns round it (off the
//                   thing: about the target, the middle of the view)
//   wheel           zooms about the point under the pointer: the whole view is scaled about that point, so it -- and
//                   everything on the line of sight through it -- stays under the pointer, and the eye never passes
//                   through what it is zooming at (off the thing: the ground under the pointer, else the point of the
//                   line of sight at the target's depth -- the atlas's zoomAt)
//   right / middle drag, Shift+drag      pans: the point grabbed follows the pointer
//   two fingers     pinch zooms about the point between them, and pans
//   fly(to)         eases there (yaw, pitch, r, target), as the atlas's camera flies
//
// The state is the atlas's: `target`, `yaw`, `pitch` (+ looks down), `r` (eye to target). `pick(raycaster, ndc)` -- the
// page's -- returns the world point it hits (a THREE.Vector3) or null; without one only the ground is picked.
import * as THREE from "three";

const UP = new THREE.Vector3(0, 1, 0);

export function createNav(camera, dom, opts = {}) {
  const o = { rotate: .006, wheel: .001, minR: .005, maxR: 5000, ground: 0, clip: true, pick: null, ...opts };
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), plane = new THREE.Plane();
  const f = new THREE.Vector3(), right = new THREE.Vector3(), up = new THREE.Vector3(), eye = new THREE.Vector3();
  const t1 = new THREE.Vector3(), t2 = new THREE.Vector3();
  const nav = {
    target: new THREE.Vector3(), yaw: 0, pitch: .3, r: 5, to: null, enabled: true,
    // f (the line of sight), right, up -- yaw 0, pitch 0 looks along -z
    basis() {
      const cp = Math.cos(this.pitch);
      f.set(Math.sin(this.yaw) * cp, -Math.sin(this.pitch), -Math.cos(this.yaw) * cp).normalize();
      right.crossVectors(f, UP).normalize(); up.crossVectors(right, f);
      return { f, right, up };
    },
    eye(out = new THREE.Vector3()) { this.basis(); return out.copy(this.target).addScaledVector(f, -this.r); },
    // set from an eye position and a point looked at (what a page's framing writes)
    lookAt(from, at) {
      this.to = null; this.target.copy(at);
      t1.subVectors(from, at); this.r = Math.max(1e-6, t1.length());
      this.pitch = Math.asin(THREE.MathUtils.clamp(t1.y / this.r, -1, 1)); this.yaw = Math.atan2(-t1.x, t1.z);
      this.apply();
    },
    // the pose as it would be looking from `from` at `at` (for fly)
    poseOf(from, at) {
      const d = new THREE.Vector3().subVectors(from, at), r = Math.max(1e-6, d.length());
      return { target: at.clone(), r, pitch: Math.asin(THREE.MathUtils.clamp(d.y / r, -1, 1)), yaw: Math.atan2(-d.x, d.z) };
    },
    fly(to) {
      const T = { target: this.target.clone(), yaw: this.yaw, pitch: this.pitch, r: this.r, ...to };
      T.target = T.target.clone();
      let d = T.yaw - this.yaw; d = ((d + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI; T.yaw = this.yaw + d;
      this.to = T;
    },
    orbit(dx, dy) { this.to = null; this.yaw += dx * o.rotate; this.pitch = THREE.MathUtils.clamp(this.pitch + dy * o.rotate, -1.55, 1.55); },
    // ...about a world point: it keeps its place in the eye's frame (so on the page) and the view turns round it
    orbitAbout(dx, dy, p) {
      this.eye(eye); this.basis(); t1.subVectors(p, eye);
      const v = [t1.dot(right), t1.dot(up), t1.dot(f)];
      this.orbit(dx, dy); this.basis();
      eye.copy(p).addScaledVector(right, -v[0]).addScaledVector(up, -v[1]).addScaledVector(f, -v[2]);
      this.target.copy(eye).addScaledVector(f, this.r);
    },
    // scale the whole view about a world point by k (< 1: closer): the eye slides along its line to it
    zoomAbout(k, p) {
      this.to = null;
      k = THREE.MathUtils.clamp(this.r * k, o.minR, o.maxR) / this.r;
      if (p) this.target.sub(p).multiplyScalar(k).add(p);
      this.r *= k;
    },
    // move the view by (dx, dy) pixels, as seen at `depth` (default: the target's): what lies there follows the pointer
    pan(dx, dy, depth = this.r) {
      this.to = null; this.basis();
      const w = depth * 2 * Math.tan(THREE.MathUtils.degToRad(camera.getEffectiveFOV()) / 2) / (dom.clientHeight || 1);
      this.target.addScaledVector(right, -dx * w).addScaledVector(up, dy * w);
    },
    // write the pose into the camera (and, with `clip`, near/far to suit the distance)
    apply() {
      this.eye(eye); camera.position.copy(eye); camera.up.copy(UP); camera.lookAt(this.target);
      if (o.clip) { camera.near = Math.max(1e-3, this.r / 250); camera.far = Math.max(100, this.r * 20); camera.updateProjectionMatrix(); }
      camera.updateMatrixWorld();
    },
    // per frame: ease a flight, write the pose; returns whether it still moves
    update(dt = 1 / 60) {
      let moving = false;
      if (this.to) {
        const k = 1 - Math.exp(-dt * 10), T = this.to;
        this.yaw += (T.yaw - this.yaw) * k; this.pitch += (T.pitch - this.pitch) * k; this.r += (T.r - this.r) * k;
        this.target.lerp(T.target, k); moving = true;
        if (Math.abs(T.yaw - this.yaw) + Math.abs(T.pitch - this.pitch) < 1e-4 && Math.abs(T.r - this.r) < T.r * 1e-4 && this.target.distanceTo(T.target) < T.r * 1e-4) {
          Object.assign(this, { yaw: T.yaw, pitch: T.pitch, r: T.r }); this.target.copy(T.target); this.to = null;
        }
      }
      this.apply();
      return moving;
    },
    // the point under page pixel (x, y) (client coordinates): { point, hit } -- `hit` "pick" (the page's thing), "ground",
    // or null (nothing: the point is then the line of sight's at the target's depth)
    pointAt(x, y) {
      const b = dom.getBoundingClientRect();
      ndc.set((x - b.left) / b.width * 2 - 1, 1 - (y - b.top) / b.height * 2);
      this.apply(); ray.setFromCamera(ndc, camera);
      const p = o.pick?.(ray, ndc);
      if (p) return { point: p.clone(), hit: "pick" };
      if (o.ground != null) {
        plane.set(UP, -o.ground);
        const g = ray.ray.intersectPlane(plane, t2);
        // (only the ground nearer than the target's depth: beyond it -- past the thing shown -- a zoom would carry the
        // eye out past the thing)
        if (g && this.depthOf(g) < this.r) return { point: g.clone(), hit: "ground" };
      }
      this.basis(); const s = this.r / Math.max(1e-6, ray.ray.direction.dot(f));
      return { point: ray.ray.origin.clone().addScaledVector(ray.ray.direction, s), hit: null };
    },
    depthOf(p) { this.eye(eye); this.basis(); return t1.subVectors(p, eye).dot(f); },
    dispose() { for (const [n, h, x] of handlers) dom.removeEventListener(n, h, x); },
  };

  // ---- the pointer ------------------------------------------------------------------------------------------------
  const pointers = new Map(); let pivot = null, grab = null, pinch = null, wheelAt = null;
  const mid = () => { const [a, b] = [...pointers.values()]; return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, Math.hypot(a[0] - b[0], a[1] - b[1])]; };
  const down = (e) => {
    if (!nav.enabled) return;
    dom.setPointerCapture?.(e.pointerId); pointers.set(e.pointerId, [e.clientX, e.clientY]); wheelAt = null;
    if (pointers.size === 1) {
      const at = nav.pointAt(e.clientX, e.clientY);
      pivot = at.hit === "pick" ? at.point : null;               // (turning: only about the thing itself, else the middle)
      grab = at.hit ? at.point : null;                           // (panning: what was grabbed, the ground too)
    } else if (pointers.size === 2) {
      const [x, y, d] = mid(), at = nav.pointAt(x, y); pinch = { x, y, d, p: at.point };
    }
  };
  const move = (e) => {
    const was = pointers.get(e.pointerId);
    if (!was || !nav.enabled) return;
    const dx = e.clientX - was[0], dy = e.clientY - was[1];
    if (pointers.size === 2) {
      pointers.set(e.pointerId, [e.clientX, e.clientY]);
      const [x, y, d] = mid();
      if (pinch) { nav.pan(x - pinch.x, y - pinch.y, Math.max(o.minR, nav.depthOf(pinch.p))); if (d > 0) nav.zoomAbout(pinch.d / d, pinch.p); pinch.x = x; pinch.y = y; pinch.d = d; }
      return;
    }
    pointers.set(e.pointerId, [e.clientX, e.clientY]);
    if (e.shiftKey || e.buttons === 2 || e.buttons === 4) nav.pan(dx, dy, grab ? Math.max(o.minR, nav.depthOf(grab)) : nav.r);
    else if (pivot) nav.orbitAbout(dx, dy, pivot);
    else nav.orbit(dx, dy);
  };
  const lift = (e) => { pointers.delete(e.pointerId); if (pointers.size < 2) pinch = null; if (!pointers.size) pivot = grab = null; };
  // (one wheel turn after another at the same spot keeps the same point: it stays put, and nothing is picked again)
  const wheel = (e) => {
    if (!nav.enabled) return;
    e.preventDefault();
    const dy = e.deltaMode === 1 ? e.deltaY * 33 : e.deltaMode === 2 ? e.deltaY * 400 : e.deltaY;
    const now = performance.now();
    if (!wheelAt || Math.abs(wheelAt.x - e.clientX) > 2 || Math.abs(wheelAt.y - e.clientY) > 2 || now - wheelAt.t > 400) wheelAt = { x: e.clientX, y: e.clientY, p: nav.pointAt(e.clientX, e.clientY).point };
    wheelAt.t = now;
    nav.zoomAbout(Math.exp(dy * o.wheel), wheelAt.p);
  };
  const handlers = [["pointerdown", down], ["pointermove", move], ["pointerup", lift], ["pointercancel", lift],
    ["wheel", wheel, { passive: false }], ["contextmenu", (e) => e.preventDefault()]];
  for (const [n, h, x] of handlers) dom.addEventListener(n, h, x);
  dom.style.touchAction = "none";
  return nav;
}

// a pick for createNav: the nearest visible mesh among `roots` (objects or a function returning them) the ray hits
export function meshPick(roots) {
  return (ray) => {
    const list = (typeof roots === "function" ? roots() : roots).filter(Boolean);
    if (!list.length) return null;
    for (const h of ray.intersectObjects(list, true)) {
      if (!h.object.isMesh) continue;
      let o = h.object, seen = true;
      while (o) { if (!o.visible) { seen = false; break; } o = o.parent; }
      if (seen) return h.point;
    }
    return null;
  };
}

// a pick for figures drawn in a shader (composite.js: no triangles for a ray to meet): each stands in a COLUMN, `cols()`
// [{ x, z, r, y0, y1 }], and the nearest column the ray enters is hit where it enters
export function columnPick(cols) {
  return (ray) => {
    const o = ray.ray.origin, d = ray.ray.direction, a = d.x * d.x + d.z * d.z;
    let best = Infinity;
    for (const c of cols()) {
      if (a < 1e-12) continue;
      const ox = o.x - c.x, oz = o.z - c.z, b = ox * d.x + oz * d.z, q = b * b - a * (ox * ox + oz * oz - c.r * c.r);
      if (q < 0) continue;
      const t = (-b - Math.sqrt(q)) / a, y = o.y + d.y * t;
      if (t > 0 && t < best && y >= c.y0 && y <= c.y1) best = t;
    }
    return best < Infinity ? o.clone().addScaledVector(d, best) : null;
  };
}
// any of several picks: the nearest point of those that hit
export function anyPick(...picks) {
  return (ray, ndc) => {
    let best = null, bd = Infinity;
    for (const p of picks) { const h = p(ray, ndc); if (h) { const dd = h.distanceTo(ray.ray.origin); if (dd < bd) { bd = dd; best = h; } } }
    return best;
  };
}

// AN ORBITCONTROLS STAND-IN, for the lab pages written for three's OrbitControls (statuary, wardrobe, menagerie, grove,
// landscape_lab): they put the camera somewhere, `controls.target.set(...)`, `controls.update()` -- a pose so written is
// taken up at the next update, and from then on the view is createNav's; `addEventListener("start", fn)` hears a drag or
// a wheel begin (OrbitControls' "start"). `nav`: the createNav underneath. The page calls update() every frame.
export function navControls(camera, dom, opts = {}) {
  const nav = createNav(camera, dom, opts), target = new THREE.Vector3(), seenEye = new THREE.Vector3(NaN, NaN, NaN), seenAt = new THREE.Vector3(NaN, NaN, NaN);
  const starts = [], start = () => { if (nav.enabled) for (const fn of starts) fn({ type: "start" }); };
  dom.addEventListener("pointerdown", start); dom.addEventListener("wheel", start, { passive: true });
  let last = performance.now();
  return {
    nav, target, enableDamping: false,
    get enabled() { return nav.enabled; }, set enabled(v) { nav.enabled = v; },
    update(dt) {
      const now = performance.now(); dt = dt ?? Math.min(.1, (now - last) / 1000); last = now;
      if (!camera.position.equals(seenEye) || !target.equals(seenAt)) nav.lookAt(camera.position.clone(), target.clone());   // (the page placed it)
      const moving = nav.update(dt);
      seenEye.copy(camera.position); target.copy(nav.target); seenAt.copy(target);
      return moving;
    },
    addEventListener(n, fn) { if (n === "start") starts.push(fn); },
    removeEventListener(n, fn) { const i = starts.indexOf(fn); if (i >= 0) starts.splice(i, 1); },
    dispose() { nav.dispose(); dom.removeEventListener("pointerdown", start); dom.removeEventListener("wheel", start); },
  };
}
