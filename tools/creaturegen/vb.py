# vb.py OUTDIR names(comma) views(comma) [--fly] [--walk=T] [--zoom=z] [--tag=x]
#  one browser: each bird shown in turn (assets.html show), views captured, a contact sheet per bird OUTDIR/<tag><name>.png
import sys, json, base64, io
sys.path.insert(0, "/home/martin/store/apps/multiverse/build")
import headless
from PIL import Image, ImageDraw
out, names, views = sys.argv[1], sys.argv[2].split(","), sys.argv[3]
opt = {a.split("=")[0][2:]: (a.split("=")[1] if "=" in a else "1") for a in sys.argv[4:] if a.startswith("--")}
zoom = float(opt.get("zoom", "1")); tag = opt.get("tag", ""); fly = "fly" in opt; walk = float(opt.get("walk", "0"))
fam = opt.get("fam", "birds")
first = names[0]
# (views "h:<view>": a close-up on the head -- centred on the sculpt's skull, from its size)
HC = {}
for nm in names:
    try:
        dd = json.load(open(f"/home/martin/store/apps/multiverse/assets/creatures/{fam}/{nm}.json"))
        sk = next((q for q in dd["sculpt"]["shape"] if q["id"] in ("skull", "head")), None)
        rr = sk["r"] if isinstance(sk["r"], list) else [sk["r"]] * 3
        HC[nm] = [0, sk["c"][1], sk["c"][0] + .3 * rr[0], max(rr) * 7.5 * float(opt.get("hz", "1"))]   # (the viewer stands it facing +z: root x -> world z)
    except Exception as e: HC[nm] = None
js = """(async()=>{const sl=(ms)=>new Promise(r=>setTimeout(r,ms));
for(let i=0;i<300;i++){if(window.__assets)break;await sl(1000);}
const A=window.__assets;const THREE=await import('three');const out={};const logs=[];
const oi=console.info;console.info=(...a)=>{logs.push(a.join(' '));oi(...a)};
const ow=console.warn;console.warn=(...a)=>{logs.push('WARN '+a.join(' '));ow(...a)};
const oe=console.error;console.error=(...a)=>{logs.push('ERR '+a.join(' '));oe(...a)};
const cv=[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0];
const names=%s;const HC=%s;
for(const nm of names){const n0=logs.length;
 if(%s){document.getElementById('fly').checked=true;}
 if(%f>0){document.getElementById('walk').checked=true;}
 A.show('creatures/%s/'+nm);
 for(let i=0;i<400;i++){if(logs.slice(n0).some(l=>l.startsWith('bodies: ')))break;await sl(500);}
 await sl(1500+%f*1000);
 if(%f>0){document.getElementById('walk').checked=false;}
 const box2=new THREE.Box3();A.scene.traverse(o=>{if(o.isMesh&&o.visible&&o.geometry&&o.type!=='GridHelper')box2.expandByObject(o)});
 const C=box2.getCenter(new THREE.Vector3()),S=box2.getSize(new THREE.Vector3());let d=(Math.max(S.x,S.y,S.z)*1.3+1)*%f;const CC=%s;if(CC){C.set(CC[0],CC[1],CC[2]);d=CC[3];}
 const P={low:[d*.8,-d*.3,d*.45],side:[0,0,d],front:[d,.05*d,0],top:[0,d,.01],q:[d*.7,d*.45,d*.7],back:[-d,.1*d,0],under:[.3*d,-d*.6,.5*d],rq:[-d*.7,d*.35,d*.7],tail:[-d*.2,.15*d,-d*.9]};
 const res={};
 for(const k of '%s'.split(',')){let p=P[k],Cv=C;if(k.startsWith('h:')){const h=HC[nm];Cv=new THREE.Vector3(h[0],h[1],h[2]);const dd=h[3]/d,p0=P[k.slice(2)];p=[-p0[2]*dd,p0[1]*dd,p0[0]*dd];}
  A.nav.lookAt(new THREE.Vector3(Cv.x+p[0],Cv.y+p[1],Cv.z+p[2]),Cv);
  await sl(350);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));res[k]=cv.toDataURL('image/png');}
 out[nm]={res,logs:logs.slice(n0).filter(l=>/bodies:|sculpt|WARN|ERR/.test(l)).slice(0,6),err:(document.getElementById('err')||{}).innerText};
}
return JSON.stringify(out);})()""" % (json.dumps(names), json.dumps(HC), "true" if fly else "false", walk, fam, walk, walk, zoom, opt.get('c','null'), views)
r = headless.run_page(f"assets.html?a=creatures/{fam}/{first}" + ("&fly=1" if fly else "") + opt.get("q", ""), ready="document.readyState === 'complete'", result=js,
                      flags=["--enable-unsafe-webgpu", "--enable-features=Vulkan", "--use-angle=vulkan", "--window-size=" + opt.get("win", "1300,800")], timeout=600, log=("log" in opt))
r = json.loads(r) if isinstance(r, str) else (print(repr(r)[:1500]) or exit(1))
for nm, o in r.items():
    ims = [Image.open(io.BytesIO(base64.b64decode(v.split(",")[1]))) for v in o["res"].values()]
    if "full" in opt:   # (each view on its own at full size: OUTDIR/<tag><name>_<view>.png)
        for k, im in zip(o["res"].keys(), ims): im.crop((int(im.size[0] * .18), 0, int(im.size[0] * .82), im.size[1])).convert("RGB").save(f"{out}/{tag}{nm}_{k.replace(':', '')}.png")
    W, H = ims[0].size
    # crop to the 3D view (the left panel ~ 0..300?) : keep all, scale down
    sc = .55
    cx = float(opt.get("crop", ".2")); ims = [im.crop((int(W*cx), int(H*cx*.6), int(W*(1-cx)), int(H*(1-cx*.6)))) for im in ims]; W, H = ims[0].size; sc = float(opt.get("sc", ".8"))
    tiles = [im.convert("RGB").resize((int(W * sc), int(H * sc))) for im in ims]
    cols = 2 if len(tiles) > 1 else 1
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tiles[0].width, rows * tiles[0].height), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * t.width, (i // cols) * t.height))
        ImageDraw.Draw(sheet).text(((i % cols) * t.width + 8, (i // cols) * t.height + 8), list(o["res"].keys())[i], fill="red")
    sheet.save(f"{out}/{tag}{nm}.png")
    print(nm, o["logs"], o["err"][:200])
