#!/usr/bin/env python3
# msheet.py OUT NAME SCALE [T] -- the menagerie, one animal, three cameras (side, 3/4 front, face) at SCALE metres -> OUT (tiled)
import sys, base64, json, subprocess
sys.path.insert(0, "/home/martin/store/apps/multiverse/build")
import headless
out, name, s = sys.argv[1], sys.argv[2], float(sys.argv[3]); t = sys.argv[4] if len(sys.argv) > 4 else "0"
cy = float(sys.argv[5]) if len(sys.argv) > 5 else 0.45 * s
cx = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
cams = [[cx, cy + 0.15 * s, 2.6 * s], [cx + 1.9 * s, cy + 0.6 * s, 1.7 * s], [cx + 2.4 * s, cy + 0.2 * s, 0.35 * s], [cx - 1.8 * s, cy + 0.9 * s, -1.6 * s]]
js = """(async()=>{await new Promise(r=>setTimeout(r,20000));const D=window.__dbg,res=[];const c=document.querySelector('canvas');
for(const p of %s){D.camera.position.set(p[0],p[1],p[2]);D.controls.target.set(%f,%f,0);D.controls.update();
await new Promise(r=>setTimeout(r,1500));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));res.push(c.toDataURL('image/png'));}
return JSON.stringify(res);})()""" % (json.dumps(cams), cx, cy)
r = json.loads(headless.run_page(f"menagerie.html?only={name}&nobar&t={t}", ready="window.__ready === true", result=js,
    flags=["--enable-unsafe-webgpu", "--enable-features=Vulkan", "--use-angle=vulkan", "--window-size=700,520"], timeout=400))
fs = []
for i, v in enumerate(r):
    f = f"{out[:-4]}_{i}.png"; open(f, "wb").write(base64.b64decode(v.split(",")[1])); fs.append(f)
subprocess.run(["python3", "/home/martin/store/apps/multiverse/tools/creaturegen/sc/carn/sheet.py", out] + fs)
