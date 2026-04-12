function showPanel(a){var w=a.willingness||.5;document.getElementById("pHead").innerHTML="<b>"+a.name+"</b>";document.getElementById("pBody").innerHTML="意愿:"+(w*100).toFixed(1)+"%";document.getElementById("panel").classList.add("open")}
function renderDrugs(){
  var q=document.getElementById('drugSearch').value.toLowerCase();
  var list=DRUGS;
  if(currentCat!=='全部')list=list.filter(function(d){return d.cat===currentCat});
  if(q)list=list.filter(function(d){return(d.name+d.generic+d.indications.join('')).toLowerCase().indexOf(q)>=0});
  document.getElementById('drugGrid').innerHTML=list.map(function(d){
    var hi=DRUGS.indexOf(d);var hasC=d.china!=='未申请'&&d.china!=='申请中';
    return '<div class="drug-card" onclick="selectDrug('+hi+')">'
      +'<div class="dc-status '+(hasC?'dc-china':'dc-fda')+'">'+(hasC?'已进入 '+d.china:'FDA '+d.fda)+'</div>'
      +'<div class="dc-category">'+d.cat+'</div>'
      +'<div class="dc-name">'+d.name+'</div>'
      +'<div class="dc-generic">'+d.generic+' · '+d.company+'</div>'
      +'<div class="dc-tags">'+d.indications.slice(0,3).map(function(x){return '<span class="dc-tag">'+x+'</span>'}).join('')+'</div>'
      +'<div class="dc-tags" style="margin-top:.4rem"><span class="dc-tag" style="color:var(--cyan)">'+d.mechanism+'</span></div>'
      +'<button class="dc-select">选择此药品 →</button></div>';
  }).join('');
}
function filterCat(cat,btn){currentCat=cat;document.querySelectorAll('.drug-filters button').forEach(function(b){b.classList.remove('active')});btn.classList.add('active');renderDrugs()}
function filterDrugs(){renderDrugs()}
function selectDrug(idx){
  selectedDrug=DRUGS[idx];
  document.getElementById('cfgPrice').value=Math.round(selectedDrug.price_us*0.15/12);
  var info=document.getElementById('selectedDrugInfo');
  info.style.display='block';
  info.innerHTML='<div style="display:flex;align-items:center;gap:1rem"><div style="font-size:2rem">💊</div><div><div style="font-size:1.1rem;font-weight:700">'+selectedDrug.name+' ('+selectedDrug.generic+')</div><div style="font-size:.85rem;color:var(--dim)">'+selectedDrug.company+' · '+selectedDrug.cat+'</div></div></div>';
  go('config');
}
function runSimulation(){
  if(!selectedDrug){alert('请先选择药品');return}
  var btn=document.querySelector('.sim-btn');
  btn.textContent='⏳ 1801 Agent仿真中...';btn.disabled=true;
  setTimeout(function(){generateResults();btn.textContent='🚀 启动1801 Agent仿真';btn.disabled=false;go('results')},1200);
}
function generateResults(){
  var d=selectedDrug;var comp=parseInt(document.getElementById('cfgCompetitors').value)||4;
  var dims=[
    {name:'流行病学',emoji:'🧬',score:.7+Math.random()*.12,color:'#06b6d4',sub:[{n:'疾病负担',s:.75+Math.random()*.1,items:[d.indications[0]+'负担高','未满足需求大']},{n:'人群分析',s:.7+Math.random()*.12,items:['患病率充足','患者池大']},{n:'RWE',s:.65+Math.random()*.12,items:['RWE可用']},{n:'结局',s:.7+Math.random()*.1,items:['终点改善']}]},
    {name:'临床评估',emoji:'🩺',score:.65+Math.random()*.12,color:'#10b981',sub:[{n:'疗效',s:.7+Math.random()*.12,items:['ORR良好']},{n:'安全性',s:.6+Math.random()*.12,items:['SAE中等']},{n:'指南',s:.65+Math.random()*.12,items:['可推荐']},{n:'操作',s:.6+Math.random()*.1,items:['可行']}]},
    {name:'市场评估',emoji:'📊',score:.6+Math.random()*.12,color:'#f59e0b',sub:[{n:'竞争',s:Math.max(.3,.7-comp*.06),items:[comp+'个竞品']},{n:'渠道',s:.6+Math.random()*.12,items:['DTP可及']},{n:'商业化',s:.65+Math.random()*.1,items:['推广可行']},{n:'容量',s:.6+Math.random()*.12,items:['TAM充足']}]},
    {name:'定价评估',emoji:'💰',score:.58+Math.random()*.12,color:'#ef4444',sub:[{n:'价值',s:.6+Math.random()*.12,items:['支撑定价']},{n:'竞争',s:.55+Math.random()*.12,items:['可比']},{n:'准入',s:.55+Math.random()*.12,items:['可谈判']},{n:'国际',s:.6+Math.random()*.1,items:['10-15%']}]},
    {name:'药物学',emoji:'⚗️',score:.6+Math.random()*.1,color:'#8b5cf6',sub:[{n:'药代',s:.65+Math.random()*.1,items:['PK良好']},{n:'药效',s:.65+Math.random()*.1,items:['验证']},{n:'毒理',s:.55+Math.random()*.12,items:['可接受']},{n:'制剂',s:.55+Math.random()*.1,items:['可行']}]},
    {name:'药物经济学',emoji:'📐',score:.55+Math.random()*.12,color:'#eab308',sub:[{n:'成本',s:.55+Math.random()*.12,items:['待验证']},{n:'预算',s:.5+Math.random()*.12,items:['可控']},{n:'质量',s:.65+Math.random()*.1,items:['可用']},{n:'HTA',s:.55+Math.random()*.12,items:['待完善']}]},
    {name:'医保评估',emoji:'📋',score:.5+Math.random()*.12,color:'#ec4899',sub:[{n:'准入',s:.55+Math.random()*.12,items:['通道']},{n:'报销',s:.45+Math.random()*.12,items:['影响']},{n:'基金',s:.45+Math.random()*.12,items:['压力']},{n:'DRG',s:.5+Math.random()*.1,items:['待评']}]}
  ];
  var avg=dims.reduce(function(s,x){return s+x.score},0)/dims.length;
  var sw=.6+Math.random()*.25;var peak=Math.round(2000+Math.random()*3000);
  document.getElementById('resultDrugDesc').textContent=d.name+'('+d.generic+') · '+d.company+' · 1801 Agent';
  var summary=[{v:peak.toLocaleString(),l:'峰值处方量/月',c:'var(--cyan)'},{v:(25+Math.random()*20).toFixed(1)+'%',l:'峰值渗透率',c:'var(--green)'},{v:(3+Math.random()*8).toFixed(1)+'亿',l:'24月总收入',c:'var(--purple)'},{v:(sw*100).toFixed(1)+'%',l:'患者意愿',c:'var(--orange)'},{v:avg.toFixed(3),l:'综合得分',c:'var(--cyan)'},{v:avg>.65?'✅推荐':'⚠️有条件',l:'建议',c:avg>.65?'var(--green)':'var(--orange)'}];
  document.getElementById('resultsSummary').innerHTML=summary.map(function(r){return '<div class="rs-card"><div class="rs-val" style="color:'+r.c+'">'+r.v+'</div><div class="rs-lbl">'+r.l+'</div></div>'}).join('');
  window._dims=dims;
  document.getElementById('expertRow').innerHTML=dims.map(function(d,i){return '<div class="expert-chip" style="--ec:'+d.color+'" onclick="showDim('+i+')"><div class="ec-emoji">'+d.emoji+'</div><div class="ec-name" style="color:'+d.color+'">'+d.name+'</div><div class="ec-score" style="color:'+d.color+'">'+d.score.toFixed(3)+'</div><div class="ec-bar"><div style="width:'+Math.round(d.score*100)+'%;background:'+d.color+'"></div></div></div>'}).join('');
  document.getElementById('compScore').innerHTML='<div style="font-size:.9rem;color:var(--dim)">7维度综合</div><div style="font-size:3rem;font-weight:900;background:linear-gradient(135deg,var(--cyan),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent">'+avg.toFixed(3)+'</div><div style="margin-top:.4rem;font-weight:600;color:'+(avg>.65?'var(--green)':'var(--orange)')+'">'+(avg>.65?'✅推荐上市':'⚠️有条件推荐')+'</div>';
  var cl=[{n:'积极采纳',c:Math.round(sw*750),color:'#10b981'},{n:'谨慎观望',c:Math.round((1-sw)*700+100),color:'#f59e0b'},{n:'中立',c:8,color:'#64748b'},{n:'怀疑',c:2,color:'#ef4444'}];
  var tot=cl.reduce(function(s,x){return s+x.c},0);
  document.getElementById('clusterRow').innerHTML=cl.map(function(c){var pct=((c.c/tot)*100).toFixed(1);var r=42,circ=2*Math.PI*r,off=circ*(1-c.c/tot);return '<div class="cluster-item"><div class="ci-ring" style="color:'+c.color+'"><svg width="90" height="90" viewBox="0 0 90 90"><circle cx="45" cy="45" r="'+r+'" stroke="'+c.color+'20" fill="none" stroke-width="5"/><circle cx="45" cy="45" r="'+r+'" stroke="'+c.color+'" fill="none" stroke-width="5" stroke-linecap="round" stroke-dasharray="'+circ+'" stroke-dashoffset="'+off+'" style="transition:stroke-dashoffset 2s"/></svg>'+pct+'%</div><div style="color:'+c.color+';font-weight:600;font-size:.9rem">'+c.n+'</div><div style="color:var(--dim);font-size:.8rem">'+c.c+'人</div></div>'}).join('');
  drawChart(peak);
}
function showDim(i){
  var d=window._dims[i];
  document.getElementById('mHead').innerHTML='<div style="font-size:2.5rem">'+d.emoji+'</div><div><h2 style="color:'+d.color+'">'+d.name+'评估</h2><div style="color:var(--dim)">'+d.score.toFixed(3)+'</div></div>';
  var b='<div class="m-section"><h4>📋 子维度</h4>';
  d.sub.forEach(function(s){b+='<div style="margin-bottom:.5rem"><div style="display:flex;justify-content:space-between;font-size:.85rem"><span style="font-weight:600">'+s.n+'</span><span style="color:'+d.color+';font-weight:700">'+s.s.toFixed(2)+'</span></div><div style="height:4px;background:var(--border);border-radius:2px;overflow:hidden"><div style="width:'+Math.round(s.s*100)+'%;height:100%;background:'+d.color+';border-radius:2px"></div></div><div style="margin-top:.2rem">'+s.items.map(function(x){return '<div style="font-size:.72rem;color:var(--dim)">• '+x+'</div>'}).join('')+'</div></div>'});
  b+='</div>';document.getElementById('mBody').innerHTML=b;document.getElementById('modalBg').classList.add('open');
}
function closeModal(){document.getElementById('modalBg').classList.remove('open')}
function drawChart(peak){
  var c=document.getElementById('chartC'),ctx=c.getContext('2d'),W=c.width,H=c.height;
  var p={t:35,r:35,b:45,l:65},pw=W-p.l-p.r,ph=H-p.t-p.b;
  ctx.clearRect(0,0,W,H);
  var ms=[{m:1,pv:Math.round(peak*.05)},{m:3,pv:Math.round(peak*.12)},{m:6,pv:Math.round(peak*.25)},{m:9,pv:Math.round(peak*.45)},{m:12,pv:Math.round(peak*.6)},{m:15,pv:Math.round(peak*.75)},{m:18,pv:Math.round(peak*.85)},{m:21,pv:Math.round(peak*.93)},{m:24,pv:peak}];
  var mx=peak*1.15;
  ctx.strokeStyle='rgba(148,163,184,.08)';
  for(var i=0;i<=5;i++){var y=p.t+ph*i/5;ctx.beginPath();ctx.moveTo(p.l,y);ctx.lineTo(W-p.r,y);ctx.stroke()}
  ms.forEach(function(d,i){var x=p.l+(i/(ms.length-1))*pw,bh=(d.pv/mx)*ph,y=p.t+ph-bh;
    ctx.fillStyle='rgba(6,182,212,.3)';ctx.beginPath();ctx.roundRect(x-18,y,36,bh,5);ctx.fill();
    ctx.fillStyle='#e2e8f0';ctx.font='bold 10px Inter';ctx.textAlign='center';ctx.fillText(d.pv.toLocaleString(),x,y-5);
    ctx.fillStyle='#64748b';ctx.font='10px Inter';ctx.fillText('M'+d.m,x,H-p.b+16);
  });
  ctx.beginPath();ctx.strokeStyle='#10b981';ctx.lineWidth=2;
  ms.forEach(function(d,i){var x=p.l+(i/(ms.length-1))*pw,y=p.t+ph-(d.pv/mx)*ph;i?ctx.lineTo(x,y):ctx.moveTo(x,y)});
  ctx.stroke();
  ms.forEach(function(d,i){var x=p.l+(i/(ms.length-1))*pw,y=p.t+ph-(d.pv/mx)*ph;ctx.beginPath();ctx.arc(x,y,3,0,6.28);ctx.fillStyle='#10b981';ctx.fill()});
}
function initParticles(){
  window._particlesInit=true;
  var c=document.getElementById('pCanvas'),ctx=c.getContext('2d'),W,H;
  function rs(){W=c.width=c.parentElement.clientWidth;H=c.height=c.parentElement.clientHeight}rs();window.addEventListener('resize',rs);
  var rng=function(s){return function(){s=(s*16807)%2147483647;return(s-1)/2147483646}}(42);
  var agents=[],N=400;
  var sn=['王','李','张','刘','陈','赵','周','吴'],gn=['明','华','丽','伟','芳','强','静','磊'];
  var sps=['肿瘤科','呼吸科','胸外科','消化科'],tiers=['三甲','三甲','二甲'];
  var atts=['早期采纳者','早期多数','晚期多数'];
  var ins=['城镇职工','城镇居民','新农合','自费'],econs=['高收入','中等收入','低收入'];
  var eN=['流行病学','临床','市场','定价','药物学','药物经济','医保'];
  var eC=['#06b6d4','#10b981','#f59e0b','#ef4444','#8b5cf6','#eab308','#ec4899'];
  for(var i=0;i<N;i++){
    var r=rng(),type,color,w,name,info;
    if(i<80){
      type='doctor';color='#3b82f6';
      name=sn[Math.floor(rng()*sn.length)]+gn[Math.floor(rng()*gn.length)];
      var att=atts[Math.floor(rng()*atts.length)];
      w=att==='早期采纳者'?rng()*.2+.75:rng()*.2+.45;
      info={type:'doctor',name,specialty:sps[Math.floor(rng()*sps.length)],tier:tiers[Math.floor(rng()*tiers.length)],exp:Math.floor(rng()*25)+5,attitude:att,willingness:w};
    }else if(i<320){
      w=Math.max(.1,Math.min(.9,.45+rng()*.3-.1));
      var tp=w>.65?'enthusiast':w>.4?'cautious':'skeptic';
      color=tp==='enthusiast'?'#10b981':tp==='cautious'?'#f59e0b':'#ef4444';
      name=sn[Math.floor(rng()*sn.length)]+(rng()>.5?'先生':'女士');
      info={type:'patient',name,age:Math.floor(rng()*50)+25,gender:rng()>.5?'男':'女',insurance:ins[Math.floor(rng()*ins.length)],econ:econs[Math.floor(rng()*econs.length)],willingness:w};
      type=tp;
    }else{
      var ei=Math.floor(rng()*7);
      type='expert';color=eC[ei];
      name=sn[Math.floor(rng()*sn.length)]+['教授','博士','研究员'][Math.floor(rng()*3)];
      w=.5+rng()*.35;
      info={type:'expert',expertType:eN[ei]+'专家',name,dimScore:w.toFixed(3),color:eC[ei]};
    }
    var angle=rng()*Math.PI*2,dist=rng()*Math.min(W,H)*.38;
    agents.push({x:W/2+Math.cos(angle)*dist,y:H/2+Math.sin(angle)*dist,vx:(rng()-.5)*.18,vy:(rng()-.5)*.18,r:type==='expert'?2.5:type==='doctor'?2:rng()+1,color:color,info:info,alpha:rng()*.3+.5});
  }
  var hov=null;
  function draw(){
    ctx.clearRect(0,0,W,H);
    agents.forEach(function(p,i){
      p.x+=p.vx+Math.sin(Date.now()*.0008+p.x*.004)*.06;
      p.y+=p.vy+Math.cos(Date.now()*.0008+p.y*.004)*.06;
      var cx=W/2,cy=H/2,mr=Math.min(W,H)*.4;
      var dx=p.x-cx,dy=p.y-cy,d=Math.sqrt(dx*dx+dy*dy);
      if(d>mr){p.x=cx+dx/d*mr;p.y=cy+dy/d*mr;p.vx*=-.3;p.vy*=-.3}
      var isH=hov===i;
      ctx.beginPath();ctx.arc(p.x,p.y,isH?p.r*3:p.r,0,6.28);
      ctx.fillStyle=p.color;ctx.globalAlpha=isH?1:p.alpha;ctx.fill();
      if(isH){ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.globalAlpha=.6;ctx.stroke()}
    });
    ctx.globalAlpha=1;requestAnimationFrame(draw);
  }
  draw();
  c.addEventListener('mousemove',function(e){
    var rect=c.getBoundingClientRect();
    var mx=(e.clientX-rect.left)*(W/rect.width),my=(e.clientY-rect.top)*(H/rect.height);
    hov=null;
    for(var i=0;i<agents.length;i++){
      var dx=agents[i].x-mx,dy=agents[i].y-my;
      if(dx*dx+dy*dy<(agents[i].r+5)*(agents[i].r+5)){hov=i;break}
    }
    c.style.cursor=hov!==null?'pointer':'crosshair';
  });
  c.addEventListener('click',function(){
    if(hov!==null)showPanel(agents[hov].info);
  });
}
function closePanel(){document.getElementById("panel").classList.remove("open")}initDrugPage();
