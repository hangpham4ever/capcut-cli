// Chữ "nhảy": mỗi chữ cái đổi cỡ/nghiêng/hoa-thường ngẫu nhiên theo seed ?v=
(function(){const v=+(new URLSearchParams(location.search).get('v')||0);let s=v*9301+49297;
const r=()=>{s=(s*9301+49297)%233280;return s/233280};
document.querySelectorAll('.jit').forEach(el=>{const t=el.textContent;el.textContent='';
 for(const ch of t){const sp=document.createElement('span');sp.style.display='inline-block';
  if(ch===' '){sp.innerHTML='&nbsp;';el.appendChild(sp);continue}
  let c=ch; if(v&&r()<0.14) c=(ch===ch.toUpperCase()?ch.toLowerCase():ch.toUpperCase());
  const sc=v?0.88+r()*0.34:1, rot=v?(r()-0.5)*10:0, ty=v?(r()-0.5)*10:0;
  sp.textContent=c; sp.style.transform=`translateY(${ty}px) rotate(${rot}deg) scale(${sc})`; el.appendChild(sp);}})})();
