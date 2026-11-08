import "./shim.mjs";
const R = "/home/martin/store/apps/multiverse/";
const S = await import(R + "species.js"), B = await import(R + "bodyspec.js");
const d = S.A(process.argv[2] ?? "frog"); const o = B.sculptOf(d);
console.log(Object.keys(o)); for (const k of Object.keys(o)) if (o[k] && typeof o[k] === "object" && !Array.isArray(o[k])) console.log(k, Object.keys(o[k]).slice(0, 20));
