const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1440}});
const W='file://'+(process.env.WORK||process.cwd())+'/';
const A={bg:'demo/a_bg.jpg',clip:'Clip 441 || 21/11/2026',l1:'Tóc – móng – máu – quần áo cũ',l2:'Bùa ngải dùng DNA của mình',hook:'CẨN THẬN',
 art1:'💇💅🩸',b1:'Không cho ai<br>tóc, móng, máu',art2:'📿🙏',b2:'Đọc Kinh<br>Lăng Nghiêm'};
const B={bg:'demo/b_bg.jpg',t:'KHI BỊ BỎ BÙA NGẢI',w:'TẠI SAO !?',k1:'VÌ',x1:'bùa ngải dùng DNA: tóc, móng tay, máu, quần áo cũ của mình',k2:'NÊN',x2:'không cho ai, giữ thân bình thường, đọc Kinh Lăng Nghiêm'};
for(const [name,file,q] of [['A','styleA.html',A],['B','styleB.html',B]]){
 for(let v=0;v<12;v++){await pg.goto(W+file+'?'+new URLSearchParams({...q,v:String(v)}));await pg.evaluate(()=>document.fonts.ready);await pg.waitForTimeout(250);
  await pg.screenshot({path:`${process.env.WORK||process.cwd()}/out/${name}_${String(v).padStart(2,'0')}.png`});}}
await b.close();})();
