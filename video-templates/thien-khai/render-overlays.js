const {chromium}=require('playwright');const fs=require('fs');const W=process.env.WORK;
const segs=JSON.parse(fs.readFileSync(W+'/segments.json'));
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1440}});
fs.mkdirSync(W+'/ov',{recursive:true});let c='',srt='';const ts=s=>{const m=Math.floor(s/60),x=s%60;return `00:${String(m).padStart(2,'0')}:${x.toFixed(3).padStart(6,'0').replace('.',',')}`};
for(let i=0;i<segs.length;i++){const [a,e,k,sub]=segs[i];await pg.goto('file://'+W+'/styleC.html?'+new URLSearchParams({k:String(k),sub}));
 await pg.evaluate(()=>document.fonts.ready);await pg.waitForTimeout(250);const f=`${W}/ov/${String(i).padStart(2,'0')}.png`;
 await pg.screenshot({path:f,omitBackground:true});c+=`file '${f}'\nduration ${(e-a).toFixed(3)}\n`;srt+=`${i+1}\n${ts(a)} --> ${ts(e)}\n${sub}\n\n`;}
c+=`file '${W}/ov/${String(segs.length-1).padStart(2,'0')}.png'\n`;fs.writeFileSync(W+'/ov/list.txt',c);fs.writeFileSync(W+'/phude.srt',srt);await b.close();})();
