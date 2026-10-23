# The WebGPU port

The target architecture is WebGPU with shaders written in **WGSL**. This note records what has been proven to
work, the traps found on the way, and how a change is checked without a screen; `?probe=corner` (or `shapes`, `sides`, `stencil`, `crowd`, `surface`, `scene`, `fixed`) runs one
section on its own. Two rules the harness learned the hard way: a probe render target needs
`stencilBuffer: true` or three builds no stencil state at all and every stencil test silently passes, and the
FIRST frame after something new enters the scene can be dropped while three builds its pipeline -- so a
measurement is taken on the second.

## The spike

`webgpu_lab.html` is the banner engine in miniature: nine capsules as one instanced draw, a quad per part fitted
to that part's projection, the silhouette cut by the 2D uneven capsule, and the exact ray-versus-round-cone hit
giving the fragment its own depth. It exists because those are the four things the port could fail on:

| risk | how it is done in WebGPU | status |
| --- | --- | --- |
| raw WGSL instead of node graphs | `wgslFn` | works |
| a fragment writing its own depth | `material.depthNode` → `@builtin(frag_depth)` | works |
| per-instance rows reaching vertex **and** fragment | `attribute()` + `varying()` | works |
| the silhouette cut-out | `opacityNode` + `alphaTest` (not a module-scope `Discard`) | works |

The depth claim is not taken on faith. `?dbg=cross` renders a red bar with a blue spear whose *midpoint* is
behind the bar but whose *surface* passes a metre and a half in front of it. With honest per-pixel depth the
spear cuts a notch through the bar; with the flat card depth of a quad (`?dbg=crossflat`) the bar stays
unbroken. The two pictures differ, so the depth is real.

Stages, for bisecting a failure: `?dbg=col` (instancing and attributes only) → `?dbg=cut` (plus the silhouette)
→ no flag (plus per-pixel depth). `?src=1` posts the generated WGSL.

## Traps found

- **The import map needs `three/webgpu`.** `three.tsl.js` imports that bare specifier internally; without it the
  page dies on "Failed to resolve module specifier" before anything runs.
- **A `wgslFn` exposes only the FIRST function in its source.** Helpers must be their own `wgslFn` passed as
  includes: `wgslFn(code, [helperA, helperB])`. Pack several `fn`s into one string and everything after the
  first is silently swallowed — the material then draws nothing, with no error.
- **WebGPU clip space runs z from 0 to 1.** Depth is `c.z / c.w`, with none of GL's `* 0.5 + 0.5`.
- **`WebGPURenderer` falls back to WebGL without saying so**, and under that backend every `wgslFn` evaluates to
  zero — which reads exactly like a broken shader. The page prints the backend for that reason; if it says
  `WebGL (fallback!)`, nothing about the WGSL below it means anything.
- **Keep the harness out of the browser path.** The headless reporting hook posts to `/report`, which does not
  exist in a browser — and a rejected `fetch` is not caught by `try/catch`, so it arrives as an unhandled
  rejection and the page's own error handler shows "Failed to fetch" over the real page. Anything that talks to
  the harness is gated on `?probe`.
- **Anything sampled from a render target is upside down too**, for the same reason: a plane's `v` runs from
  the bottom and the target's rows run from the top. The palace's paintings -- views of the world hung in its
  frames -- came out inverted, and the fix is the canvas' own UVs, flipped once where it is built.
- **A render target reads back from the TOP.** WebGL's `readPixels` handed back the bottom row first; WebGPU's
  readback starts at v = 1, because its render targets have their origin there. Every tool that turned a baked
  tile back into a picture flipped it by hand for the WebGL order, so on the switch the exported PNGs in
  `texture/` came out upside down -- silently, since a tiling pattern still looks like a tiling pattern.
  `readTile` now turns the rows back once, where the readback happens, so its callers keep the one order they
  were written for. (And the export's headless Chromium needs the WebGPU flags: under `--use-angle=swiftshader`
  the page runs and reads back black.)
- **Port the maths exactly.** A "roughly equivalent" round cone made every ray miss, so every pixel fell back to
  the midpoint depth and nine solids rendered as nine flat cards. `sdUnevenCapsule2`, `hitCone` and `approachT`
  in the spike are line-for-line ports of `banner.js`.

## The performance lab

`perf_lab.html` answers the question the port raises next: what does a banner's pixel actually cost? Every
banner it draws is placed to COVER THE WHOLE VIEW, so one banner is one full screen of that shader's work, and
leaving them standing (N) stacks the layers. The catalogue runs from the cheapest pixel a GPU can draw (a
texture read) through the 2D silhouettes a banner cuts -- circle, box, rounded box, uneven capsule, triangle,
hexagon, star, heart, vesica, cross, ellipse -- to the exact 3D hits the world's engines really pay for
(sphere, round cone, ellipsoid, closed form, with the surface normal) and seven sphere-traced fields for
comparison. K puts 1/2/4/8 copies into one banner -- the nearest hit wins for the closed forms, the figures'
own smooth union for the traced ones: the same pixel asked about more shapes, which is what a crowded figure
costs. T switches the surface texture through four tiers (none, procedural, one planar fetch, triplanar), and
one square in five of that texture is a HOLE -- the pixel is thrown away, so a cut-out surface pays for its
shape twice and shows whatever stands behind it.

Everything is drawn INSTANCED: one draw per kind of banner (plus its stencil bound pass) and one for all the
walls, with each banner's anchor, colour and turn as per-instance attributes and the quad itself built in the
vertex shader. A mesh per banner is what the lab started with, and with a few dozen solids three's per-object
work -- matrices, bind groups, uniform writes -- grew past the fragment work the lab exists to measure. The
scene is described in `perf_lab.json` (how many of each shape, how many walls, and a bound on how many
silhouettes may overlap along any one direction, so a frame time can be compared with another frame time).

**A banner's quad faces its own solid, not the screen; `?probe=corner` (or `shapes`, `sides`, `stencil`, `crowd`, `surface`, `scene`, `fixed`) runs one
section on its own. Two rules the harness learned the hard way: a probe render target needs
`stencilBuffer: true` or three builds no stencil state at all and every stencil test silently passes, and the
FIRST frame after something new enters the scene can be dropped while three builds its pipeline -- so a
measurement is taken on the second.** Turned to face the camera, the quad stands at an
angle to the eye->solid line wherever the solid is off-centre, the tangent cone cuts its plane obliquely, and a
quad fitted to the head-on silhouette slices the solid off -- worse the further from the middle of the screen
it stands. Widening for that angle works but the widening runs away as a solid leaves the view (quads that
swell as you turn). Facing the eye, the fit is the exact head-on circle at every angle: the smallest quad that
covers the solid, and a size that does not change when you turn on the spot. The self-check proves it by
measuring the same solid through a wider quad and a narrower one, at several turns and viewpoints.

The background is a sunset gradient TEXTURE that scrolls one pixel a frame -- a still frame is a lie on a
tiled GPU, and to the eye. The readout gives fps, ms/frame, the frame's own JavaScript (cpu), the GPU's time
for its draws (WebGPU timestamps), and fragments per second at the current layer count. `?probe=1` builds
every entry headless and reports what each covered, so a shape that will not compile is caught without a
screen; `?probe=corner` (or `shapes`, `sides`, `stencil`, `crowd`, `surface`, `scene`, `fixed`) runs one
section on its own. Two rules the harness learned the hard way: a probe render target needs
`stencilBuffer: true` or three builds no stencil state at all and every stencil test silently passes, and the
FIRST frame after something new enters the scene can be dropped while three builds its pipeline -- so a
measurement is taken on the second.

## Two things that bite on WebGPU and did not on WebGL

- **GPU timestamps must be resolved, every frame.** `renderer.backend.trackTimestamp = true` gives you
  `info.render.timestamp`, but three keeps a pool of queries and fills it unless
  `renderer.resolveTimestampsAsync()` is called; after that the readings stop and the warnings start. Ask the
  adapter for the `timestamp-query` feature first, and resolve what you asked for.
- **No WebGPU means no shaders at all, not slower shaders.** Every shader in this world is WGSL, so when three
  falls back to WebGL they evaluate to nothing and the world comes up blank -- which looks like a bug in the
  world rather than a missing browser feature. Both `index.html` and `perf_lab.html` now say so on the page.
  Chrome and Edge have WebGPU; Firefox does not enable it by default (Nightly: `dom.webgpu.enabled`).

## Parity: the port is checked against the original, not against itself

`banner_wgsl.js` is the WGSL twin of `banner.js`'s `SDF_GLSL`, and `examples/webgpu_parity.html` proves it is a
twin rather than a cousin. It evaluates twenty of the library's functions over a grid of tiles -- silhouettes,
the ray-cone hit, the part frame, the cell grids, the bark relief and each pattern -- once through the GLSL
original under `WebGLRenderer` (`?api=gl`) and once through the WGSL port under `WebGPURenderer` (`?api=gpu`),
posts both frames as hex, and `examples/webgpu_parity_diff.py` diffs them tile by tile. They currently agree
**exactly**, with a maximum difference of 0 on every tile.

Two conventions differ and must be compensated, or everything reads as broken: GL measures `gl_FragCoord.y`
from the bottom and WebGPU its `position.y` from the top, and a GL target reads back bottom-up where WebGPU
reads top-down. Both are handled in the page, so the shader bodies themselves stay identical.

Two more traps, both of which cost a run: **`ref` is a reserved word in WGSL** (three's compile error says so,
but only through `console.error`, which a headless page must intercept), and a **backtick inside a WGSL comment
ends the JavaScript template literal** it lives in -- the file then fails to parse, with an error that points
somewhere else entirely.

## Checking without a screen

Headless Chromium runs WebGPU but cannot present it, and the ways a picture normally comes back are all closed:
`--screenshot` and `drawImage` return an empty canvas, `requestAnimationFrame` never fires, and three's
`readRenderTargetPixelsAsync` waits for a device tick that never comes. Worse, merely *asking* for the canvas
swap-chain drops the WebGPU instance, after which every read fails with `Instance dropped`.

`wgprobe.js` works around all of it:

- `headlessRenderer()` — a renderer whose canvas hands back a stub webgpu context. Nothing is ever presented, so
  the instance survives.
- `probe(renderer, scene, camera, opts)` — renders one frame into a render target, copies the texture into a
  buffer with plain WebGPU, and prints it as an ASCII thumbnail plus a colour tally. `chars: [{rgb, ch}]`
  classifies each cell by nearest colour instead, which is how "which part won this pixel" is read back.
- `dumpShader(...)` — the generated WGSL.
- Both post their result to `/report`, because a headless run is killed on a wall clock rather than when the
  page is ready.

The browser flags that give a real WebGPU backend (Dawn on SwiftShader) rather than the WebGL fallback:

```
--headless=new --no-sandbox --enable-unsafe-swiftshader \
--enable-features=Vulkan,SkiaGraphite --use-webgpu-adapter=swiftshader --enable-unsafe-webgpu
```

Software rendering, so it is slow and says nothing about speed — but it answers "is this drawing what I think
it is", which was the question that used to need a human at a browser.

## The port is done

Every shader in the world is WGSL through three's node materials, and `index.html` runs on `WebGPURenderer`.
Checked file by file against the code it replaced, and then end to end:

| what | how it was checked | result |
| --- | --- | --- |
| the SDF library (`banner_wgsl.js`) | 20 functions over a tile grid, GLSL vs WGSL | identical |
| the tile patterns (`textures_wgsl.js`) | 21 tiles, the same way | identical |
| the tile bake | baked texels compared | identical |
| the instanced banner engine | one oak, same seed and camera | 0.00% of pixels differ |
| the architecture engine | one house | 0.00% (bit-identical with `?tex=off`) |
| the composite engine | a person and an owl, every PIPE switch | 0.00% |
| **the whole world** | the village, same viewpoint and clock | **0.80% of pixels differ, mean 0.78/255** |

The last 0.8% is thin-feature pixels -- a one-pixel grass stalk or a leaf's cut-out edge landing on one side of a
pixel centre rather than the other -- plus the two backends' texture filtering. Nothing structural.

`?probe=1` runs the app headless and prints the frame as ASCII; `?probe=px` posts it as pixels for comparison.
Both render one frame into a render target at a FIXED viewpoint with a pinned clock, because wind, water and
flames all move with time: two runs at different wall-clock moments differ by several percent of the frame for
no other reason.

### What the crossing cost, beyond translating the maths

Every one of these cost at least one run to find, and none of them announces itself as what it is:

- **`ref` is a reserved word.** So is anything else WGSL reserves; three's compile error says so, but only
  through `console.error`, which a headless page must intercept.
- **A backtick inside a WGSL comment ends the JavaScript template literal** it lives in. The file then fails to
  parse, pointing somewhere else entirely.
- **Three's WGSL parser rejects a function with no return type.** `fn f(...) { }` is "not a WGSL code"; give it
  `-> f32` and `return 0.0`, and consume the value with `_ =` at the call site.
- **A wgslFn exposes only the FIRST function of its source.** Helpers are separate `wgslFn`s passed as includes
  (which nest, so each lists only what it calls).
- **Three's type map knows `mat2x2`, `mat3x3`, `mat4x4` and no other matrix.** Return a `mat2x4` and the node
  has no type, after which a swizzle on one of its columns silently disappears -- `output.depth = m[1]` instead
  of `m[1].x`, and the shader fails to compile with an error that names neither.
- **A texture whose min and mag filters are both `NearestFilter` is "unfilterable"**, and three then declares no
  sampler for it: raw WGSL that samples it fails on an unresolved `<name>_sampler`. Either make it filterable or
  read it with `textureLoad`, which is what NEAREST meant anyway.
- **`screenCoordinate.y` counts from the TOP** where `gl_FragCoord.y` counted from the bottom, and **clip space
  runs z from 0 to 1**, so an unprojection takes `z = 0` for the near plane and `ndc.y = 1 - 2 * uv.y`. The
  grass fringe walks down the screen looking for the ground it grows from: with either convention taken from
  GL, it searches the wrong way and the lawn goes quietly thin.
- **`onBeforeCompile` has no equivalent.** A material that patched three's own shader becomes a subclass
  overriding `setupOutput(builder, outputNode)` -- which is where the ground's lawn and snow now go.
- **The instance transform reaches a custom vertex graph only through `positionLocal`/`normalLocal`.** A custom
  attribute is left unturned; the outline hull's inflation direction therefore rides in the geometry's `normal`
  with its length beside it in `aDirLen`.
- **A vertex stage's varyings all come from one call.** A wgslFn returns one value, so the composite engine's
  expensive vertex work returns a `mat4x4` and each varying reads a slot of that single (node-cached) call.
  Pointers do inside WGSL what GLSL's `inout` and file-scope globals did; only entry points speak TSL's types.

### What changed shape rather than language

- `Reflector` (the WebGL addon) is gone: the water and the palace mirrors use TSL's `reflector()`, which brings
  its own mirrored camera and target.
- GPU frame time comes from `renderer.info.render.timestamp` instead of `EXT_disjoint_timer_query_webgl2`.
- `readTile` is async: WebGPU has no synchronous read-back.
- `WebGLRenderTarget` is `RenderTarget` throughout, and the near pass's second output is an `mrt()` node keyed
  by the target's texture names.

## Order of the port, and where it stood


`banner.js` (the shared SDF library) → `instanced.js` → `architecture.js` and the tile bake → `composite.js`
last, being the largest (about 900 lines of shader). Roughly 2200 lines of GLSL in all.

- **The shared library — done.** `banner_wgsl.js`, agreeing with the GLSL original exactly (see Parity above).
- **The instanced banner engine (`instanced.js`) — done.** Its shaders are now WGSL through node materials: the
  quad's plane and the projected shape in the vertex stage, and one fragment function returning `(rgb, depth)`
  whose single result the material reads three ways — colour, the silhouette cut (`opacityNode` against
  `alphaTest`, a node material's discard) and the pixel's own depth. The `uInvView` uniform is gone: TSL's
  `cameraWorldMatrix` already is it.
- **The tile patterns (`textures.js` `PATTERN_GLSL`) — done.** `textures_wgsl.js`, agreeing exactly: all
  eleven patterns, their relief, and the grass blades.
- **The tile bake — done.** One WGSL full-screen pass per tile, 3 x 3 samples a texel, colour carrying the
  pattern and alpha its relief. The baked texels are identical to the GLSL bake's. `readTile` is now async:
  WebGPU has no synchronous read-back.
- **The architecture engine (`architecture.js`) — done.** The outline hull, the building material (every
  pattern branch, the tile parallax with its relief shadows, the crop cut-outs, the fruit dots, the snow) and
  the stained glass. Where the GLSL had one shader behind a wall of `#if PAT == n`, the WGSL source is
  generated per material in JavaScript, so each carries only its own branch.
- Still on GLSL: `composite.js`, `grass.js`, `foliage.js`, `paths.js`, `weather.js` and the shaders inside
  `index.html`. Until they follow, the app itself stays on WebGL — the two renderers cannot share a canvas, so
  the switch in `index.html` happens once, at the end.

### How an engine's port is checked

The same way the library was: against the code it replaces, not against itself. `examples/webgl_herd_ref.html`
draws an oak with the **pre-port** GLSL engine under WebGL; `examples/webgpu_herd.html` draws the same oak, same
seed, same camera, with the new WGSL engine under WebGPU; both post their frame and
`examples/webgpu_parity_diff.py`-style comparison reports how much differs. For the herd engine: **0.00% of
pixels**, bark parallax included, and 0.01% (a few edge pixels) with the one-pixel outline turned on, where the
two backends' derivatives disagree by a step.

For the buildings: **0.00% of pixels differ by more than a quantisation step**, and with the baked tiles
switched off (`?tex=off`, patterns evaluated per pixel) the two frames are **bit-identical**. What remains with
the tiles on — about 9% of pixels differing by under 24/255 — is the two backends' texture filtering, not the
port's arithmetic; that difference exists between GPUs too.

Three things the architecture port had to solve, worth knowing before the next file:

- **A texture in raw WGSL needs a sampler parameter**, and three supplies it when the same texture node is
  passed for both: `fn f(tex: texture_2d<f32>, samp: sampler, ...)` called as `f({ tex: node, samp: node })`.
  But a texture whose min and mag filters are both `NearestFilter` counts as *unfilterable*, and three then
  declares no sampler at all — the shader fails to compile on an unresolved `<name>_sampler`, which reads like
  a broken API and is not one.
- **The instance transform reaches a custom vertex graph only through `positionLocal` and `normalLocal`**,
  which three rewrites for an `InstancedMesh`. A custom attribute is left unturned, so the outline hull's
  inflation direction now rides in the geometry's `normal` (unit) with its length in `aDirLen` beside it --
  the hull's own surface normals were never used.
- **The building parallax now walks the view ray in world space** against the world-space pattern axes,
  instead of in the object's frame. The two frames differ by a rotation and nothing here is scaled, so the walk
  is the same one -- and this way it needs no per-instance inverse model matrix, which a node graph cannot get.

The superseded engine is not kept in the repo. The harness server maps `/ref/<file>` to a copy outside the
source tree and falls back to the app's own file, so the reference page's other imports still resolve.
