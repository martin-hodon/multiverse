const V = "file:///home/martin/store/apps/multiverse/build/vendor/";
export async function resolve(spec, ctx, next) {
  if (spec === "three" || spec === "three/webgpu") return { url: V + "vendor_three.js", shortCircuit: true };
  if (spec === "three/tsl") return { url: V + "vendor_tsl.js", shortCircuit: true };
  return next(spec, ctx);
}
