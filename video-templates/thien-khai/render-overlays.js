// Render 2 lớp cho phong cách Thiên khải động:
//  ovb/ : lớp nền + thẻ + phụ đề (thẻ bật lên khi đổi ý)  -> ovb/list.txt
//  ovt/ : lớp tựa đề động (intro 1.2s + vòng lặp 2.6s)     -> ovt/list.txt
const {chromium}=require('playwright');const fs=require('fs');
const W=process.env.WORK, DUR=+process.env.DUR, FPS=30;
const segs=JSON.parse(fs.readFileSync(W+'/segments.json'));
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1440}});
await pg.goto('file://'+W+'/styleC2.html');await pg.evaluate(()=>document.fonts.ready);
const R=async(o,f)=>{await pg.evaluate(o=>window.render(o),o);await pg.screenshot({path:f,omitBackground:true});};
let L='',n=0,prevK=0;const pad=i=>String(i).padStart(4,'0');
for(const [a,e,k,sub] of segs){
  let start=a;
  if(k!==prevK){const N=12;for(let j=1;j<=N;j++){const f=`${W}/ovb/${pad(n++)}.png`;await R({k,sub,p:j/N,part:'base'},f);L+=`file '${f}'\nduration ${(1/FPS).toFixed(4)}\n`;}start+=12/FPS;}
  const f=`${W}/ovb/${pad(n++)}.png`;await R({k,sub,p:1,part:'base'},f);L+=`file '${f}'\nduration ${Math.max(0.001,e-start).toFixed(4)}\n`;prevK=k;}
L+=`file '${W}/ovb/${pad(n-1)}.png'\n`;fs.writeFileSync(W+'/ovb/list.txt',L);
// title
const intro=[],loop=[];
for(let i=0;i<36;i++){const f=`${W}/ovt/i${pad(i)}.png`;await R({k:1,t:i/FPS,part:'title'},f);intro.push(f);}
for(let i=0;i<78;i++){const f=`${W}/ovt/l${pad(i)}.png`;await R({k:1,t:1.2+i/FPS,part:'title'},f);loop.push(f);}
let T='',c=0;const tot=Math.ceil(DUR*FPS)+2;
for(const f of intro){T+=`file '${f}'\nduration ${(1/FPS).toFixed(4)}\n`;c++;}
while(c<tot){T+=`file '${loop[(c-36)%loop.length]}'\nduration ${(1/FPS).toFixed(4)}\n`;c++;}
fs.writeFileSync(W+'/ovt/list.txt',T);await b.close();})();
