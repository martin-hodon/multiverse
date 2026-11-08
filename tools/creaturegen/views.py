# views.py OUT_PREFIX QUERY WAIT  -> OUT_PREFIX_{side,front,top,q}.png : the asset from four sides (assets.html window.__assets.nav)
import sys, json, base64
sys.path.insert(0, "/home/martin/store/apps/multiverse/build")
import headless
out, q, wait = sys.argv[1], sys.argv[2], int(sys.argv[3])
views = sys.argv[4] if len(sys.argv) > 4 else "side,front,top,q"
zoom = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--zoom=")), "1"))
aim = next((a.split("=")[1] for a in sys.argv if a.startswith("--aim=")), "0,0,0")
js = """(async()=>{{const t0=Date.now();while(Date.now()-t0<%d&&!window.__assets)await new Promise(r=>setTimeout(r,500));const TH=await import('three');let last=-1,same=0;
while(Date.now()-t0<%d){const b=new TH.Box3();window.__assets.scene.traverse(o=>{if(o.isMesh&&o.visible&&o.geometry&&o.type!=='GridHelper')b.expandByObject(o)});const z=b.isEmpty()?0:b.getSize(new TH.Vector3()).length();
let sk=false;window.__assets.scene.traverse(o=>{if(o.isSkinnedMesh&&o.visible&&(o.geometry?.attributes?.position?.count||0)>500)sk=true});if(sk&&z>0.3&&Math.abs(z-last)<1e-3*z)same++;else same=0;last=z;if(same>=3)break;await new Promise(r=>setTimeout(r,1000));}await new Promise(r=>setTimeout(r,2000));}const A=window.__assets,T=A.nav.target??null;
const V=window.__assets.view;const THREE=await import('three');
const box=new THREE.Box3();A.scene.traverse(o=>{});
const c=document.querySelectorAll('canvas');const cv=[...c].sort((a,b)=>b.width*b.height-a.width*a.height)[0];
const ctr=A.camera.position.clone();const res={};
// centre: from the current orbit (frame() put it there)
const tgt=A.nav.center?A.nav.center():null;
const box2=new THREE.Box3();A.scene.traverse(o=>{if(o.isMesh&&o.visible&&o.geometry&&!o.isGridHelper&&!(o.type==='GridHelper'))box2.expandByObject(o)});
const C=box2.getCenter(new THREE.Vector3()),S=box2.getSize(new THREE.Vector3());const d=(Math.max(S.x,S.y,S.z)*1.3+1)*%f;C.x+=%s[0];C.y+=%s[1];C.z+=%s[2];
const P={side:[0,0,d],front:[d,.05*d,0],top:[0,d,.01],q:[d*.7,d*.45,d*.7],back:[-d,.1*d,0],under:[.3*d,-d*.6,.5*d]};
for(const k of '%s'.split(',')){const p=P[k];A.nav.lookAt(new THREE.Vector3(C.x+p[0],C.y+p[1],C.z+p[2]),C);
await new Promise(r=>setTimeout(r,500));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));res[k]=cv.toDataURL('image/png');}
return JSON.stringify({res,err:document.getElementById('err').innerText,stats:document.getElementById('stats').innerText});})()""" % (wait*1000, wait*1000, zoom, "["+aim+"]", "["+aim+"]", "["+aim+"]", views)
_r = headless.run_page(q, ready="document.readyState === 'complete'", result=js, flags=["--enable-unsafe-webgpu","--enable-features=Vulkan","--use-angle=vulkan","--window-size=1300,800"], timeout=wait+150, log=("--log" in sys.argv))
if not isinstance(_r,str): print(repr(_r)[:2000]); sys.exit(1)
r = json.loads(_r)
for k, v in r.pop("res").items(): open(f"{out}_{k}.png", "wb").write(base64.b64decode(v.split(",")[1]))
print(json.dumps(r)[:400])
