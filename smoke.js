// CHIMNEY SMOKE: soft puffs rising from the chimneys of the houses whose hearth is lit, leaning with the wind,
// growing and thinning as they climb. One mesh, one draw for the whole town: every puff is a quad whose place,
// size and fade are worked out on the GPU from the time and its own phase -- nothing is touched per frame but
// one uniform. A puff is billboarded in view space (it always faces the eye) and depth-tested, so roofs and
// walls in front of it hide it.
//
//   const smoke = createSmoke(scene, [{ x, y, z }...], { seed })   // the chimney tops (architecture.js lifeOf `chimneys`)
//   smoke.update(t, { amount, light })                            // every frame: amount 0 none .. 1 the usual .. 2 a cold day; light the hour's
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec2, vec3, vec4, float, varying, uv, fract, sin, cos, smoothstep, mix, clamp, pow,
         cameraViewMatrix, cameraProjectionMatrix, renderGroup } from "three/tsl";
import { windAt, WIND as GUSTS, WIND_DIR as WIND } from "./grass.js";   // (GUSTS: its strength; WIND: its way)
import { rng } from "./flora.js";
import { SNOW } from "./foliage.js";

export const SMOKE = {
  puffs: 14,          // puffs in the air above one chimney at a time
  life: 11,           // seconds from the chimney's mouth until a puff has thinned away
  rise: 9,            // metres a puff climbs in its life
  drift: 7,           // metres the wind carries it sideways in its life
  size: [.45, 3.2],   // its width leaving the chimney, and when it has thinned
  lit: .7,            // the share of chimneys smoking all year (the rest only in winter, while the snow lies)
  color: [.78, .78, .76],
};

export function createSmoke(scene, chimneys, { seed = 7 } = {}) {
  const r = rng(seed * 31 + 5);
  // every chimney but a nested one (a stork's nest on it: index.html STORK) -- `warm` the share that smokes all year;
  // the rest are lit IN WINTER only (foliage.js SNOW: every hearth burning while the snow lies)
  const lit = chimneys.filter((c) => !c.nest).map((c) => ({ ...c, warm: r() < SMOKE.lit }));
  const n = lit.length * SMOKE.puffs;
  if (!n) return { mesh: null, update() {} };
  const corner = new Float32Array(n * 8), base = new Float32Array(n * 12), seedA = new Float32Array(n * 12), warmA = new Float32Array(n * 4), index = new Uint32Array(n * 6);
  let q = 0;
  for (const c of lit) {
    for (let k = 0; k < SMOKE.puffs; k++, q++) {
      const ph = (k + r() * .6) / SMOKE.puffs, spin = r() * 6.283, lump = r();
      for (let v = 0; v < 4; v++) {
        const i = q * 4 + v;
        corner[i * 2] = v & 1 ? .5 : -.5; corner[i * 2 + 1] = v & 2 ? .5 : -.5;
        base.set([c.x, c.y, c.z], i * 3);
        seedA.set([ph, spin, lump], i * 3);   // its phase in the cycle, its turn, its own lumps and pace
        warmA[i] = c.warm ? 1 : 0;
      }
      index.set([q * 4, q * 4 + 1, q * 4 + 3, q * 4, q * 4 + 3, q * 4 + 2], q * 6);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("corner", new THREE.BufferAttribute(corner, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(corner.map((v) => v + .5), 2));   // (the quad's own 0..1, for the shape drawn on it)
  g.setAttribute("base", new THREE.BufferAttribute(base, 3));
  g.setAttribute("seedA", new THREE.BufferAttribute(seedA, 3));
  g.setAttribute("warm", new THREE.BufferAttribute(warmA, 1));
  g.setAttribute("position", new THREE.BufferAttribute(base.slice(), 3));   // (for the bounds three asks for; the shader places the quads)
  g.setIndex(new THREE.BufferAttribute(index, 1));

  const U = { t: uniform(0), amount: uniform(1), tint: uniform(new THREE.Color(...SMOKE.color)), winter: uniform(0).setGroup(renderGroup).onRenderUpdate(() => Math.min(1, SNOW.value)) };
  const cA = attribute("corner", "vec2"), bA = attribute("base", "vec3"), sA = attribute("seedA", "vec3");
  const pace = fract(sA.z.mul(7.31)).mul(.4).add(.8);                        // 0.8 .. 1.2
  const age = fract(U.t.div(SMOKE.life).mul(pace).add(sA.x));                 // 0 at the mouth .. 1 gone
  const gust = windAt({ p: bA.xz, t: U.t }).mul(.15).add(1);              // the wind's gusts, as the grass feels them
  const climb = age.mul(SMOKE.rise).mul(age.mul(-.35).add(1.15));            // fast out of the flue, slowing as it cools
  const along = pow(age, 1.4).mul(SMOKE.drift).mul(gust).mul(GUSTS.strength);   // (laid flatter downwind in a gale: grass.js WIND)
  const wob = sin(U.t.mul(.7).add(sA.y.mul(3))).mul(age).mul(.6);
  const centre = bA.add(vec3(along.mul(WIND.x).add(wob.mul(WIND.y)), climb, along.mul(WIND.y).sub(wob.mul(WIND.x))));
  // (a winter-only chimney's puffs shrink to nothing while no snow lies: no transparent quads drawn for nothing all summer)
  const size = mix(float(SMOKE.size[0]), float(SMOKE.size[1]), pow(age, .8)).mul(attribute("warm", "float").max(U.winter.mul(1e4).min(1)));
  const turn = sA.y.add(age.mul(1.2));
  const c2 = vec2(cA.x.mul(cos(turn)).sub(cA.y.mul(sin(turn))), cA.x.mul(sin(turn)).add(cA.y.mul(cos(turn))));
  const view = cameraViewMatrix.mul(vec4(centre, 1));
  const placed = vec4(view.xy.add(c2.mul(size)), view.z, view.w);

  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(placed);
  const vFade = varying(smoothstep(0, .08, age).mul(smoothstep(1, .45, age)).mul(U.amount.min(1.5)).mul(.42).mul(mix(U.winter, float(1), attribute("warm", "float"))));
  const vLump = varying(sA.z.mul(6.283));
  const vAge = varying(age);
  // the puff: a soft round body, its edge broken by a few slow lobes so no two look alike
  const p = uv().sub(.5).mul(2);
  const ang = p.y.atan(p.x);
  const edge = sin(ang.mul(3).add(vLump)).mul(.12).add(sin(ang.mul(5).sub(vLump.mul(1.7))).mul(.07)).add(.82);
  const body = smoothstep(edge, edge.mul(.25), p.length());
  mat.colorNode = mix(U.tint.mul(.82), U.tint, vAge.add(.25).min(1));   // (darker as it leaves the flue, paler as it thins)
  mat.opacityNode = clamp(body.mul(vFade), 0, 1);
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, null, SMOKE.rise + SMOKE.drift + SMOKE.size[1]);   // (its vertices sit on the chimneys; the puffs go up and downwind of them)
  mesh.renderOrder = 4;
  mesh.name = "chimney smoke";
  mesh.userData.noMerge = true;   // (merge.js must leave it alone: its quads are placed by the shader)
  scene.add(mesh);
  return {
    mesh, count: lit.filter((c) => c.warm).length,
    update(t, { amount = 1, light = null } = {}) {   // light: the hour's colour on it (sky.js `cloud`): rose at sunset, slate at night
      U.t.value = t; U.amount.value = amount; mesh.visible = amount > .01;
      U.tint.value.setRGB(...SMOKE.color); if (light) U.tint.value.multiply(light);
    },
  };
}
