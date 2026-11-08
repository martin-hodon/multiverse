# av.py OUTDIR ITEMS [VIEWS] [--fly] [--log] [--hk=2.2]
#  ITEMS: comma list of asset paths (creatures/dinosaurs/triceratops), each optionally with :coat=N or :variant=NAME
#  VIEWS: b_q,b_side,b_front,b_top,b_under,h_q,h_side,h_front (default b_q,h_q)  -> OUTDIR/<name>[_<dress>]_<view>.png
#  One page load for all items (assets.html show()); the body is awaited after each switch (a new skinned mesh, its size steady).
import sys, json, base64, os
sys.path.insert(0, "/home/martin/store/apps/multiverse/build")
import headless
out, items = sys.argv[1], sys.argv[2].split(",")
views = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "b_q,h_q"
hk = float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--hk=")), "2.2"))
os.makedirs(out, exist_ok=True)
q = "assets.html?a=" + items[0].split(":")[0] + "&bodycache=0" + ("&fly=1" if "--fly" in sys.argv else "")
js = r"""(async()=>{const out=[],info={};try{
const t0=Date.now();while(Date.now()-t0<120000&&!window.__assets)await new Promise(r=>setTimeout(r,500));
const A=window.__assets,TH=await import('three');const sl=(ms)=>new Promise(r=>setTimeout(r,ms));const fr=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
const cv=[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0];
const PERSON=%s,PB=%f,HY=%f,WT=%f,HB=%f;const vis=(o)=>{for(let p=o;p;p=p.parent)if(!p.visible)return false;return true;};
const skins=()=>{const s=[];A.scene.traverse(o=>{if(PERSON?(o.isMesh&&!o.isInstancedMesh&&vis(o)&&(o.geometry?.attributes?.position?.count||0)>40&&!/grid|ground|floor|sky|shadow/i.test(o.name||'')&&o.geometry.type!=='PlaneGeometry'&&(o.geometry.computeBoundingSphere(),o.geometry.boundingSphere.radius<4)&&(()=>{o.updateWorldMatrix(true,false);const c=o.geometry.boundingSphere.center.clone().applyMatrix4(o.matrixWorld);return Math.hypot(c.x,c.z)<4;})()):(o.isSkinnedMesh&&o.visible&&(o.geometry?.attributes?.position?.count||0)>300))s.push(o)});return s;};
const ITEMS=%s,VIEWS=%s.split(','),HK=%f;
for(const it of ITEMS){const [path,dr]=it.split(':');const nm=path.split('/').pop()+(dr?'_'+dr.replace('=','').replace(/[^\w-]/g,''):'');const t1=Date.now();
 try{
 const before=new Set(skins().map(o=>o.geometry.uuid));
 if(path!==ITEMS[0].split(':')[0]||dr){A.show(path);}
 if(dr){const [k,v]=dr.split('=');A.pickDress(k==='coat'?{coat:+v}:{variant:v});}
 let last=-1,same=0;
 while(Date.now()-t1<150000){await sl(700);const s=skins();const fresh=s.filter(o=>!before.has(o.geometry.uuid));if(!fresh.length&&(path!==ITEMS[0].split(':')[0]||dr)){same=0;continue;}
  const b=new TH.Box3();for(const o of s)b.expandByObject(o);const z=b.isEmpty()?0:b.getSize(new TH.Vector3()).length();if(z>0&&Math.abs(z-last)<1e-3*z)same++;else same=0;last=z;if(same>=3)break;}
 if(WT>=0){for(const p of (A.person||[]))if(p&&p.an)Object.defineProperty(p.an,'wingT',{get:()=>WT,set(){},configurable:true});await sl(1500);}
 await sl(800);
 const box=new TH.Box3(),pts=[],v=new TH.Vector3();A.scene.updateMatrixWorld(true);for(const o of skins()){o.skeleton&&o.skeleton.update();const n=o.geometry.attributes.position.count,st=Math.max(1,Math.floor(n/6000));for(let i=0;i<n;i+=st){o.getVertexPosition(i,v);o.localToWorld(v);if(!PERSON)v.set(v.z,v.y,v.x);pts.push(v.clone());box.expandByPoint(v);}}
 let C=box.getCenter(new TH.Vector3()),S=box.getSize(new TH.Vector3()),M=Math.max(S.x,S.y,S.z);
 const PA=PERSON&&A.person&&A.person[0]&&A.person[0].an;if(PA){const p=PA.position;box.set(PB?new TH.Vector3(p.x-PB,0,p.z-PB):new TH.Vector3(p.x-.8,0,p.z-.6),PB?new TH.Vector3(p.x+PB,1.6+PB*.6,p.z+PB):new TH.Vector3(p.x+.8,1.9,p.z+.6));C=box.getCenter(new TH.Vector3());S=box.getSize(new TH.Vector3());M=PB?Math.max(2.4,PB*1.6):2.4;pts.length=0;pts.push(new TH.Vector3(p.x,HY,p.z+.04));}
 const zc=box.max.z-Math.max(.15,Math.min(.12*S.z,1.4));const hp=PERSON?pts.filter(p=>p.y>box.max.y-.13*S.y):pts.filter(p=>p.z>zc);const H=new TH.Vector3();for(const p of hp)H.add(p);H.multiplyScalar(1/Math.max(1,hp.length));
 const hb2=new TH.Box3();for(const p of hp)hb2.expandByPoint(p);const hs=hb2.getSize(new TH.Vector3());let hd=Math.max(.3,Math.max(hs.x,hs.y,(box.max.z-zc))*HK);if(PERSON)hd=Math.max(.45,hs.y*2.6);else H.z-=(box.max.z-zc)*.25+HB;if(HB>0)hd=Math.max(hd,HB*1.4);
 info[nm]={box:[C.x,C.y,C.z,S.x,S.y,S.z].map(v=>+v.toFixed(2)),head:[H.x,H.y,H.z].map(v=>+v.toFixed(2)),hd:+hd.toFixed(2),ms:Date.now()-t1,err:document.getElementById('err')?.innerText||''};
 const d=M*1.15+.6;
 const P={b_q:[[.75,.42,.75],d,C],b_side:[[1,.08,0],d,C],b_front:[[0,.1,1],d,C],b_back:[[0,.15,-1],d,C],b_l:[[-1,.08,0],d,C],b_top:[[.05,1,.25],d,C],b_under:[[.25,-.75,.45],d,C],
  h_q:[[.75,.35,.7],hd,H],h_front:[[0,.08,1],hd,H],h_side:[[1,.08,0],hd,H],h_l:[[-1,.08,0],hd,H]};
 for(const v of VIEWS){const p=P[v];if(!p)continue;const n=Math.hypot(...p[0]),c=p[2];A.nav.lookAt(new TH.Vector3(c.x+p[0][0]/n*p[1],c.y+p[0][1]/n*p[1],c.z+p[0][2]/n*p[1]),c.clone());
  await sl(350);await fr();const pr=c.clone().project(A.camera);(info[nm].cam=info[nm].cam||{})[v]=[A.camera.position.x,A.camera.position.y,A.camera.position.z,pr.x,pr.y].map(q=>+q.toFixed(2));out.push([nm+'_'+v,cv.toDataURL('image/png')]);}
 }catch(e){info[nm]={x:String(e.stack||e)};}
}
return JSON.stringify({out,info});}catch(e){return JSON.stringify({out,info,x:String(e.stack||e)});}})()""" % ("true" if "--person" in sys.argv else "false", float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--pbox=")), "0")), float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--hy=")), "1.66")), float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--wt=")), "-1")), float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--hb=")), "0")), json.dumps(items), json.dumps(views), hk)
_r = headless.run_page(q, ready="document.readyState === 'complete'", result=js, flags=["--enable-unsafe-webgpu", "--enable-features=Vulkan", "--use-angle=vulkan", "--window-size=1900,1200"], timeout=200 + 160 * len(items), log=("--log" in sys.argv))
if not isinstance(_r, str): print("page failed:", repr(_r)[:1500]); sys.exit(1)
try: r = json.loads(_r)
except ValueError: print("page script threw (not JSON):", _r[:1500]); sys.exit(1)
for k, v in r.pop("out"): open(f"{out}/{k}.png", "wb").write(base64.b64decode(v.split(",")[1]))
if r.get("x"): print("page script exception:", r["x"])
for k, v in r["info"].items(): print(k, json.dumps(v)[:600])
