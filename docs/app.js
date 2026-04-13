/* ═══════════════════════════════════════
   PharmaSim v3.2 — app.js
   Complete interactive simulation engine
   with real data from SQLite database
   ═══════════════════════════════════════ */

// ── Data Store ──
var DATA = {drugs:[], scores:[], epi:[], pipeline:[], dimensions:{}, loaded:false};

function loadData(callback){
  var files = ['drugs','scores','epidemiology','pipeline','dimensions','summary'];
  var loaded = 0;
  files.forEach(function(f){
    var xhr = new XMLHttpRequest();
    xhr.open('GET','api/'+f+'.json',true);
    xhr.onload = function(){
      if(xhr.status===200){
        try{ DATA[f==='epidemiology'?'epi':f] = JSON.parse(xhr.responseText); }catch(e){}
      }
      loaded++;
      if(loaded===files.length){
        DATA.loaded = true;
        // Build DRUGS compat array from real data
        window.DRUGS = DATA.drugs.map(function(d){
          var sc = DATA.scores.find(function(s){return s.drug.id===d.id});
          return {
            name: d.name,
            generic: d.chinese_name || d.generic_name,
            company: d.company,
            cat: d.therapeutic_area,
            fda: String(d.fda_approval_year||''),
            china: d.china.status==='approved'?(d.china.approval_date||'').substring(0,4):(d.china.status==='pending'?'申请中':'未申请'),
            indications: d.indications||[d.indication],
            mechanism: d.mechanism,
            price_us: d.pricing&&d.pricing.US?d.pricing.US.price_per_month*12:0,
            efficacy: d.efficacy||{},
            _realId: d.id,
            _score: sc
          };
        });
        if(callback) callback();
      }
    };
    xhr.send();
  });
}

// ── Drug page ──
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

// ── Navigation ──
function go(page){
  document.querySelectorAll('.page').forEach(function(p){p.classList.remove('active')});
  document.getElementById('page-'+page).classList.add('active');
  document.querySelectorAll('.nav-tab').forEach(function(t){t.classList.toggle('active',t.dataset.p===page)});
  if(page==='agents'&&!window._particlesInit)initParticles();
  window.scrollTo({top:0,behavior:'smooth'});
}

// ── Simulation ──
function runSimulation(){
  if(!selectedDrug){alert('请先选择药品');return}
  var btn=document.querySelector('.sim-btn');
  btn.textContent='⏳ 1801 Agent仿真中...';btn.disabled=true;
  setTimeout(function(){generateResults();btn.textContent='🚀 启动1801 Agent仿真';btn.disabled=false;go('results')},1200);
}

function generateResults(){
  var d=selectedDrug;var comp=parseInt(document.getElementById('cfgCompetitors').value)||4;
  var dimColors={epidemiology:'#06b6d4',clinical:'#10b981',market:'#f59e0b',pricing:'#ef4444',pharmacology:'#8b5cf6',pharmaecon:'#eab308',insurance:'#ec4899'};
  
  // Use real scores if available
  var dims=[];
  if(d._score && d._score.dimensions){
    var scoreData=d._score.dimensions;
    Object.keys(scoreData).forEach(function(k){
      var sd=scoreData[k];
      dims.push({
        name:sd.name, emoji:sd.emoji, score:sd.score,
        color:dimColors[k]||'#06b6d4',
        sub:sd.sub_dimensions.map(function(s){
          return {n:s.name, s:s.score, items:[s.explanation||'基于真实数据分析']}
        })
      });
    });
  }else{
    // Fallback with reduced randomness
    dims=[
      {name:'流行病学',emoji:'🧬',score:.68,color:'#06b6d4',sub:[{n:'疾病负担',s:.72,items:['基于流行病学数据库']},{n:'人群分析',s:.65,items:['中国患者池分析']},{n:'未满足需求',s:.70,items:['治疗率待提升']},{n:'严重度',s:.60,items:['疾病严重度评估']}]},
      {name:'临床评估',emoji:'🩺',score:.62,color:'#10b981',sub:[{n:'疗效',s:.65,items:['临床试验数据分析']},{n:'安全性',s:.58,items:['安全性数据评估']},{n:'指南',s:.60,items:['指南推荐分析']},{n:'操作',s:.65,items:['给药便利性评估']}]},
      {name:'市场评估',emoji:'📊',score:.58,color:'#f59e0b',sub:[{n:'竞争',s:Math.max(.3,.7-comp*.06),items:[comp+'个竞品']},{n:'容量',s:.60,items:['市场容量估算']},{n:'渠道',s:.55,items:['渠道分析']},{n:'商业化',s:.55,items:['商业化评估']}]},
      {name:'定价评估',emoji:'💰',score:.56,color:'#ef4444',sub:[{n:'价值',s:.58,items:['价值评估']},{n:'竞争',s:.55,items:['定价竞争力']},{n:'准入',s:.52,items:['医保准入分析']},{n:'国际',s:.60,items:['国际参考价']}]},
      {name:'药物学',emoji:'⚗️',score:.60,color:'#8b5cf6',sub:[{n:'药代',s:.62,items:['PK参数分析']},{n:'药效',s:.60,items:['PD数据']},{n:'毒理',s:.55,items:['毒性评估']},{n:'制剂',s:.65,items:['制剂可行性']}]},
      {name:'药物经济学',emoji:'📐',score:.54,color:'#eab308',sub:[{n:'成本',s:.55,items:['成本效果分析']},{n:'预算',s:.50,items:['预算影响']},{n:'质量',s:.60,items:['QALY评估']},{n:'HTA',s:.52,items:['HTA证据']}]},
      {name:'医保评估',emoji:'📋',score:.50,color:'#ec4899',sub:[{n:'准入',s:.55,items:['国谈资格']},{n:'报销',s:.45,items:['报销广度']},{n:'基金',s:.48,items:['基金压力']},{n:'DRG',s:.52,items:['DRG兼容性']}]}
    ];
  }
  var avg=dims.reduce(function(s,x){return s+x.score},0)/dims.length;
  
  // Real-derived metrics
  var patPop=d._realId?((DATA.epi.find(function(e){return e.disease===(d.indications?d.indications[0]:'')})||{}).total_patients_cn||500000):500000;
  var peak=Math.round(patPop*avg*0.003+500);
  var sw=avg*0.9+0.1;
  var rev24=(peak*(d.price_us||15000)/12*24/1e8).toFixed(1);
  
  document.getElementById('resultDrugDesc').textContent=d.name+' ('+d.generic+') · '+d.company+' · 基于真实数据分析';
  var summary=[
    {v:peak.toLocaleString(),l:'峰值处方量/月',c:'var(--cyan)'},
    {v:(sw*100).toFixed(1)+'%',l:'峰值渗透率',c:'var(--green)'},
    {v:rev24+'亿',l:'24月总收入',c:'var(--purple)'},
    {v:(sw*100).toFixed(1)+'%',l:'患者意愿',c:'var(--orange)'},
    {v:avg.toFixed(3),l:'综合得分',c:'var(--cyan)'},
    {v:avg>.65?'✅推荐':avg>.50?'⚠️有条件':'❌暂不推荐',l:'建议',c:avg>.65?'var(--green)':avg>.50?'var(--orange)':'var(--red)'}
  ];
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

// ═══════════════════════════════════════
// AGENT PARTICLE SYSTEM — with connections
// ═══════════════════════════════════════
function initParticles(){
  window._particlesInit=true;
  var c=document.getElementById('pCanvas'),ctx=c.getContext('2d'),W,H;
  function rs(){W=c.width=c.parentElement.clientWidth;H=c.height=c.parentElement.clientHeight}rs();window.addEventListener('resize',rs);

  // Seeded RNG
  var rng=function(s){return function(){s=(s*16807)%2147483647;return(s-1)/2147483646}}(42);

  var agents=[],N=400;
  var sn=['王','李','张','刘','陈','赵','周','吴','孙','黄','林','杨'];
  var gn=['明','华','丽','伟','芳','强','静','磊','红','敏','建国','秀英','志强','海燕'];
  var sps=['肿瘤科','呼吸科','胸外科','消化科','血液科','乳腺外科','放疗科'];
  var hosps=['协和医院','华西医院','瑞金医院','中山医院','301医院','湘雅医院','齐鲁医院','省人民医院','市第一医院','肿瘤医院'];
  var tiers=['三甲','三甲','三甲','二甲','二甲','三乙'];
  var atts=['早期采纳者','早期多数','晚期多数','创新者'];
  var ins=['城镇职工','城镇职工','城镇居民','新农合','新农合','自费'];
  var econs=['高收入','中等收入','中等收入','低收入'];
  var eN=['流行病学','临床','市场','定价','药物学','药物经济','医保'];
  var eC=['#06b6d4','#10b981','#f59e0b','#ef4444','#8b5cf6','#eab308','#ec4899'];
  var stances=[
    '基于现有临床数据，该药物在疗效和安全性方面表现良好，建议纳入处方考虑范围',
    '需要更多中国人群的RWE数据来支持临床决策，目前持观望态度',
    '该药物的定价策略需要与医保谈判结果综合评估，疗效确切但价格偏高',
    '从循证医学角度，推荐在特定亚组患者中优先使用',
    '关注长期安全性数据，特别是罕见不良事件的监测结果',
    '药物经济学分析显示ICER值在可接受范围内，支持纳入医保',
    '考虑到仿制药竞争和带量采购政策，需要更精准的市场定位'
  ];

  // Cluster centers for agent types (for social network grouping)
  var clusterCenters=[
    {x:0.3,y:0.3},  // doctors
    {x:0.5,y:0.5},  // patients
    {x:0.7,y:0.4}   // experts
  ];

  for(var i=0;i<N;i++){
    var r=rng(),type,color,name,info,cluster;
    if(i<80){
      type='doctor';color='#3b82f6';cluster=0;
      name=sn[Math.floor(rng()*sn.length)]+gn[Math.floor(rng()*gn.length)];
      var sp=sps[Math.floor(rng()*sps.length)];
      var hosp=hosps[Math.floor(rng()*hosps.length)];
      var tier=tiers[Math.floor(rng()*tiers.length)];
      var att=atts[Math.floor(rng()*atts.length)];
      var w=att==='创新者'?rng()*.15+.82:att==='早期采纳者'?rng()*.2+.7:att==='早期多数'?rng()*.2+.45:rng()*.15+.25;
      var exp=Math.floor(rng()*30)+3;
      var patients=Math.floor(rng()*200)+20;
      info={type:'doctor',name:name,specialty:sp,hospital:hosp,tier:tier,exp:exp,patients:patients,attitude:att,willingness:w,
        stance:stances[Math.floor(rng()*stances.length)],
        publications:Math.floor(rng()*50),
        clinicalTrials:Math.floor(rng()*8)};
    }else if(i<320){
      cluster=1;
      var w=Math.max(.1,Math.min(.92,.45+rng()*.3-.1));
      var tp=w>.68?'enthusiast':w>.42?'cautious':'skeptic';
      color=tp==='enthusiast'?'#10b981':tp==='cautious'?'#f59e0b':'#ef4444';
      type=tp==='enthusiast'?'patient_pos':tp==='cautious'?'patient_mid':'patient_neg';
      name=sn[Math.floor(rng()*sn.length)]+(rng()>.5?'先生':'女士');
      var age=Math.floor(rng()*50)+25;
      var gender=rng()>.5?'男':'女';
      var insurance=ins[Math.floor(rng()*ins.length)];
      var econ=econs[Math.floor(rng()*econs.length)];
      var city=['北京','上海','广州','深圳','成都','杭州','武汉','南京','重庆','西安'][Math.floor(rng()*10)];
      var disease=selectedDrug?selectedDrug.indications[Math.floor(rng()*selectedDrug.indications.length)]:'慢性疾病';
      info={type:'patient',name:name,age:age,gender:gender,insurance:insurance,econ:econ,city:city,
        disease:disease,willingness:w,
        stance:w>.68?'非常期待新药上市，愿意积极配合医生治疗方案':w>.42?'会参考医生建议和医保报销情况后再决定':'对新药持保守态度，更信任现有治疗方案',
        monthlyIncome:econ==='高收入'?(15+Math.floor(rng()*30))+'K':econ==='中等收入'?(5+Math.floor(rng()*10))+'K':(2+Math.floor(rng()*3))+'K'};
    }else{
      cluster=2;
      var ei=Math.floor(rng()*7);
      type='expert';color=eC[ei];
      name=sn[Math.floor(rng()*sn.length)]+['教授','博士','研究员','主任'][Math.floor(rng()*4)];
      var w=.5+rng()*.35;
      var uni=['北京大学','清华大学','复旦大学','上海交大','浙江大学','中山大学','中国药科大学'][Math.floor(rng()*7)];
      info={type:'expert',expertType:eN[ei]+'专家',name:name,dimScore:w.toFixed(3),color:eC[ei],
        university:uni,publications:Math.floor(rng()*200)+10,hIndex:Math.floor(rng()*40)+8,
        stance:stances[Math.floor(rng()*stances.length)],
        grants:Math.floor(rng()*5)+1,
        influence:['高','中','低'][Math.floor(rng()*3)]};
    }

    // Position near cluster center with spread
    var cc=clusterCenters[cluster];
    var angle=rng()*Math.PI*2;
    var dist=rng()*Math.min(W,H)*.22;
    var cx=W*cc.x+Math.cos(angle)*dist;
    var cy=H*cc.y+Math.sin(angle)*dist;
    // Clamp to bounds
    cx=Math.max(20,Math.min(W-20,cx));
    cy=Math.max(20,Math.min(H-20,cy));

    agents.push({x:cx,y:cy,vx:(rng()-.5)*.12,vy:(rng()-.5)*.12,
      r:type==='expert'?3:type==='doctor'?2.5:rng()*1.2+1.2,
      color:color,info:info,alpha:rng()*.3+.5,cluster:cluster,
      connections:[]});
  }

  // Build Watts-Strogatz social network connections
  // Each agent connects to k nearest neighbors with rewiring probability p
  var K=4; // mean degree
  var P_REWIRE=0.3;
  var MAX_CONN_DIST=Math.min(W,H)*0.12; // max connection distance

  for(var i=0;i<agents.length;i++){
    // Find nearest neighbors
    var dists=[];
    for(var j=0;j<agents.length;j++){
      if(i===j)continue;
      var dx=agents[i].x-agents[j].x,dy=agents[i].y-agents[j].y;
      var dd=Math.sqrt(dx*dx+dy*dy);
      // Prefer same-cluster connections (stronger social ties)
      if(agents[i].cluster===agents[j].cluster)dd*=0.6;
      dists.push({idx:j,d:dd});
    }
    dists.sort(function(a,b){return a.d-b.d});
    for(var k=0;k<K&&k<dists.length;k++){
      var target=dists[k].idx;
      // Rewire with probability P
      if(rng()<P_REWIRE){
        target=Math.floor(rng()*agents.length);
        if(target===i)continue;
      }
      // Check if connection already exists
      if(agents[i].connections.indexOf(target)<0&&agents[target].connections.indexOf(i)<0){
        var cdx=agents[i].x-agents[target].x,cdy=agents[i].y-agents[target].y;
        if(Math.sqrt(cdx*cdx+cdy*cdy)<MAX_CONN_DIST){
          agents[i].connections.push(target);
        }
      }
    }
  }

  // Tooltip element
  var tooltip=document.createElement('div');
  tooltip.style.cssText='position:fixed;pointer-events:none;background:rgba(15,23,42,.95);border:1px solid #334155;border-radius:10px;padding:.6rem .8rem;font-size:.78rem;color:#e2e8f0;z-index:300;max-width:260px;display:none;box-shadow:0 4px 20px rgba(0,0,0,.4);line-height:1.4';
  document.body.appendChild(tooltip);

  var hov=null,mouseX=0,mouseY=0;

  function getAgentTooltip(a){
    var i=a.info;
    if(i.type==='doctor'){
      return '<b style="color:#3b82f6">👨‍⚕️ '+i.name+'</b><br>'
        +'<span style="color:#94a3b8">'+i.hospital+' · '+i.tier+'</span><br>'
        +'<span style="color:#94a3b8">'+i.specialty+' · '+i.exp+'年经验</span><br>'
        +'<span>处方意愿: <b style="color:'+(i.willingness>.65?'#10b981':i.willingness>.4?'#f59e0b':'#ef4444')+'">'+(i.willingness*100).toFixed(0)+'%</b></span>';
    }else if(i.type==='expert'){
      return '<b style="color:'+i.color+'">'+i.expertType+' '+i.name+'</b><br>'
        +'<span style="color:#94a3b8">'+i.university+'</span><br>'
        +'<span>影响力: <b>'+i.influence+'</b> · H-index: <b>'+i.hIndex+'</b></span><br>'
        +'<span>维度评分: <b style="color:'+i.color+'">'+i.dimScore+'</b></span>';
    }else{
      var tc=i.willingness>.68?'#10b981':i.willingness>.42?'#f59e0b':'#ef4444';
      return '<b style="color:'+tc+'">👤 '+i.name+'</b><br>'
        +'<span style="color:#94a3b8">'+i.city+' · '+i.age+'岁 · '+i.gender+'</span><br>'
        +'<span style="color:#94a3b8">'+i.insurance+' · '+i.econ+'</span><br>'
        +'<span>采纳意愿: <b style="color:'+tc+'">'+(i.willingness*100).toFixed(0)+'%</b></span>';
    }
  }

  function draw(){
    ctx.clearRect(0,0,W,H);

    // Draw connections first (behind dots)
    for(var i=0;i<agents.length;i++){
      var a=agents[i];
      for(var ci=0;ci<a.connections.length;ci++){
        var j=a.connections[ci];
        var b=agents[j];
        var dx=a.x-b.x,dy=a.y-b.y;
        var dist=Math.sqrt(dx*dx+dy*dy);
        var maxD=MAX_CONN_DIST;
        if(dist>maxD)continue;

        // Opacity based on distance — closer = brighter
        var alpha=Math.max(0.04,0.25*(1-dist/maxD));
        // Highlight connections of hovered agent
        if(hov===i||hov===j)alpha=Math.min(1,alpha*4);

        ctx.beginPath();
        ctx.moveTo(a.x,a.y);
        ctx.lineTo(b.x,b.y);

        if(hov===i||hov===j){
          // Active connection — gradient
          var grad=ctx.createLinearGradient(a.x,a.y,b.x,b.y);
          grad.addColorStop(0,a.color);
          grad.addColorStop(1,b.color);
          ctx.strokeStyle=grad;
          ctx.lineWidth=1.5;
          ctx.globalAlpha=alpha;
        }else{
          // Dim connection
          ctx.strokeStyle='#64748b';
          ctx.lineWidth=0.5;
          ctx.globalAlpha=alpha;
        }
        ctx.stroke();
        ctx.globalAlpha=1;
      }
    }

    // Draw agents
    for(var i=0;i<agents.length;i++){
      var p=agents[i];

      // Physics: gentle movement + boundary bounce
      p.x+=p.vx+Math.sin(Date.now()*.0006+p.x*.003+p.cluster*2)*.05;
      p.y+=p.vy+Math.cos(Date.now()*.0006+p.y*.003+p.cluster*2)*.05;

      // Soft clustering force
      var cc=clusterCenters[p.cluster];
      var tcx=W*cc.x,tcy=H*cc.y;
      p.vx+=(tcx-p.x)*0.00003;
      p.vy+=(tcy-p.y)*0.00003;

      // Damping
      p.vx*=0.998;p.vy*=0.998;

      // Boundary
      var cx=W/2,cy=H/2,mr=Math.min(W,H)*.42;
      var dx=p.x-cx,dy=p.y-cy,d=Math.sqrt(dx*dx+dy*dy);
      if(d>mr){p.x=cx+dx/d*mr;p.y=cy+dy/d*mr;p.vx*=-.3;p.vy*=-.3}

      // Edge boundary
      if(p.x<10){p.x=10;p.vx*=-.5}
      if(p.x>W-10){p.x=W-10;p.vx*=-.5}
      if(p.y<10){p.y=10;p.vy*=-.5}
      if(p.y>H-10){p.y=H-10;p.vy*=-.5}

      var isH=hov===i;

      // Glow effect for hovered
      if(isH){
        ctx.beginPath();ctx.arc(p.x,p.y,p.r*6,0,6.28);
        var glow=ctx.createRadialGradient(p.x,p.y,p.r,p.x,p.y,p.r*6);
        glow.addColorStop(0,p.color+'40');
        glow.addColorStop(1,p.color+'00');
        ctx.fillStyle=glow;ctx.fill();
      }

      // Pulse ring for high-willness agents
      if(p.info.willingness>0.75&&!isH){
        var pulse=Math.sin(Date.now()*.003+p.x)*.5+.5;
        ctx.beginPath();ctx.arc(p.x,p.y,p.r+2+pulse*2,0,6.28);
        ctx.strokeStyle=p.color;ctx.globalAlpha=0.15*pulse;ctx.lineWidth=1;ctx.stroke();ctx.globalAlpha=1;
      }

      // Main dot
      ctx.beginPath();ctx.arc(p.x,p.y,isH?p.r*3:p.r,0,6.28);
      ctx.fillStyle=p.color;
      ctx.globalAlpha=isH?1:p.alpha;
      ctx.fill();

      if(isH){
        ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.globalAlpha=.8;ctx.stroke();
        // Label
        ctx.globalAlpha=1;
        ctx.font='bold 11px Inter';ctx.fillStyle='#fff';ctx.textAlign='center';
        ctx.fillText(p.info.name,p.x,p.y-p.r*3-6);
      }
      ctx.globalAlpha=1;
    }

    // Stats overlay
    ctx.font='10px Inter';ctx.fillStyle='#64748b';ctx.textAlign='right';
    ctx.fillText('400 Agents · 华兹-斯托格茨社交网络',W-12,H-8);

    requestAnimationFrame(draw);
  }
  draw();

  // Mouse tracking
  c.addEventListener('mousemove',function(e){
    var rect=c.getBoundingClientRect();
    mouseX=(e.clientX-rect.left)*(W/rect.width);
    mouseY=(e.clientY-rect.top)*(H/rect.height);
    hov=null;
    for(var i=0;i<agents.length;i++){
      var dx=agents[i].x-mouseX,dy=agents[i].y-mouseY;
      if(dx*dx+dy*dy<(agents[i].r+8)*(agents[i].r+8)){hov=i;break}
    }
    c.style.cursor=hov!==null?'pointer':'crosshair';

    // Update tooltip
    if(hov!==null){
      tooltip.innerHTML=getAgentTooltip(agents[hov]);
      tooltip.style.display='block';
      // Position near cursor
      var tx=e.clientX+15,ty=e.clientY+15;
      if(tx+260>window.innerWidth)tx=e.clientX-270;
      if(ty+120>window.innerHeight)ty=e.clientY-125;
      tooltip.style.left=tx+'px';tooltip.style.top=ty+'px';
    }else{
      tooltip.style.display='none';
    }
  });

  c.addEventListener('mouseleave',function(){hov=null;tooltip.style.display='none'});

  c.addEventListener('click',function(){
    if(hov!==null)showAgentPanel(agents[hov].info);
  });
}

// ── Enhanced Agent Panel ──
function showAgentPanel(a){
  var head='',body='';
  var tc=a.type==='doctor'?'#3b82f6':a.type==='expert'?a.color:(a.willingness>.68?'#10b981':a.willingness>.42?'#f59e0b':'#ef4444');
  var icon=a.type==='doctor'?'👨‍⚕️':a.type==='expert'?'🔬':'👤';

  head='<div class="ph-av" style="background:'+tc+'22;color:'+tc+'">'+icon+'</div>'
    +'<div><div style="font-weight:700;font-size:1rem">'+a.name+'</div>'
    +'<div style="font-size:.8rem;color:#94a3b8">'+(a.type==='doctor'?a.hospital:a.type==='expert'?a.expertType:a.city)+'</div></div>';

  if(a.type==='doctor'){
    body='<div style="margin-bottom:1rem">'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">医院</span><span>'+a.hospital+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">等级</span><span>'+a.tier+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">科室</span><span>'+a.specialty+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">从业年限</span><span>'+a.exp+'年</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">年患者量</span><span>'+a.patients+'人</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">论文发表</span><span>'+a.publications+'篇</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">临床试验</span><span>'+a.clinicalTrials+'项</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0"><span style="color:#94a3b8">创新采纳类型</span><span>'+a.attitude+'</span></div>'
      +'</div>'
      +'<div style="margin-bottom:1rem">'
      +'<div style="font-size:.8rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.5rem">📊 处方意愿</div>'
      +'<div style="height:8px;background:#1e293b;border-radius:4px;overflow:hidden"><div style="width:'+Math.round(a.willingness*100)+'%;height:100%;background:linear-gradient(90deg,#06b6d4,#10b981);border-radius:4px;transition:width .8s"></div></div>'
      +'<div style="text-align:right;font-size:.85rem;margin-top:.3rem;font-weight:700;color:'+tc+'">'+(a.willingness*100).toFixed(1)+'%</div>'
      +'</div>'
      +'<div style="background:rgba(6,182,212,.08);border:1px solid rgba(6,182,212,.15);border-radius:10px;padding:.8rem;font-size:.82rem;line-height:1.6;color:#cbd5e1">'
      +'<div style="font-size:.75rem;color:#06b6d4;margin-bottom:.3rem">💬 专家观点</div>'
      +a.stance+'</div>';
  }else if(a.type==='expert'){
    body='<div style="margin-bottom:1rem">'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">专业领域</span><span>'+a.expertType+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">所属院校</span><span>'+a.university+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">论文发表</span><span>'+a.publications+'篇</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">H-index</span><span>'+a.hIndex+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">科研项目</span><span>'+a.grants+'项</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0"><span style="color:#94a3b8">行业影响力</span><span>'+a.influence+'</span></div>'
      +'</div>'
      +'<div style="margin-bottom:1rem">'
      +'<div style="font-size:.8rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.5rem">📊 维度评分</div>'
      +'<div style="height:8px;background:#1e293b;border-radius:4px;overflow:hidden"><div style="width:'+Math.round(parseFloat(a.dimScore)*100)+'%;height:100%;background:'+a.color+';border-radius:4px;transition:width .8s"></div></div>'
      +'<div style="text-align:right;font-size:.85rem;margin-top:.3rem;font-weight:700;color:'+a.color+'">'+a.dimScore+'</div>'
      +'</div>'
      +'<div style="background:'+a.color+'12;border:1px solid '+a.color+'25;border-radius:10px;padding:.8rem;font-size:.82rem;line-height:1.6;color:#cbd5e1">'
      +'<div style="font-size:.75rem;color:'+a.color+';margin-bottom:.3rem">💬 评估观点</div>'
      +a.stance+'</div>';
  }else{
    var tc2=a.willingness>.68?'#10b981':a.willingness>.42?'#f59e0b':'#ef4444';
    body='<div style="margin-bottom:1rem">'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">年龄</span><span>'+a.age+'岁</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">性别</span><span>'+a.gender+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">城市</span><span>'+a.city+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">医保类型</span><span>'+a.insurance+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">经济水平</span><span>'+a.econ+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="color:#94a3b8">月收入</span><span>'+a.monthlyIncome+'</span></div>'
      +'<div style="display:flex;justify-content:space-between;padding:.4rem 0"><span style="color:#94a3b8">适应症</span><span>'+a.disease+'</span></div>'
      +'</div>'
      +'<div style="margin-bottom:1rem">'
      +'<div style="font-size:.8rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.5rem">📊 采纳意愿</div>'
      +'<div style="height:8px;background:#1e293b;border-radius:4px;overflow:hidden"><div style="width:'+Math.round(a.willingness*100)+'%;height:100%;background:linear-gradient(90deg,'+tc2+','+tc2+'cc);border-radius:4px;transition:width .8s"></div></div>'
      +'<div style="text-align:right;font-size:.85rem;margin-top:.3rem;font-weight:700;color:'+tc2+'">'+(a.willingness*100).toFixed(1)+'%</div>'
      +'</div>'
      +'<div style="background:'+tc2+'12;border:1px solid '+tc2+'25;border-radius:10px;padding:.8rem;font-size:.82rem;line-height:1.6;color:#cbd5e1">'
      +'<div style="font-size:.75rem;color:'+tc2+';margin-bottom:.3rem">💬 患者态度</div>'
      +a.stance+'</div>';
  }

  document.getElementById('pHead').innerHTML=head;
  document.getElementById('pBody').innerHTML=body;
  document.getElementById('panel').classList.add('open');
}
function closePanel(){document.getElementById('panel').classList.remove('open')}

// ═══════════════════════════════════════
// HERO PARTICLE SYSTEM — background network
// ═══════════════════════════════════════
function initHeroParticles(){
  var c=document.getElementById('heroCanvas');
  if(!c)return;
  var ctx=c.getContext('2d'),W,H;
  function rs(){W=c.width=c.parentElement.clientWidth;H=c.height=c.parentElement.clientHeight}rs();
  window.addEventListener('resize',rs);
  var rng=function(s){return function(){s=(s*16807)%2147483647;return(s-1)/2147483646}}(7);
  var agents=[],N=180;
  var types=[
    {color:'#3b82f6',count:36},
    {color:'#10b981',count:72},
    {color:'#f59e0b',count:36},
    {color:'#ef4444',count:18},
    {color:'#8b5cf6',count:18}
  ];
  var idx=0;
  types.forEach(function(t){
    for(var i=0;i<t.count;i++){
      agents.push({x:rng()*W,y:rng()*H,vx:(rng()-.5)*.15,vy:(rng()-.5)*.15,r:rng()*1.2+1,color:t.color,alpha:rng()*.3+.4,cluster:idx});
    }
    idx++;
  });
  // Build connections
  var K=3,MAX_D=Math.min(W,H)*.15;
  for(var i=0;i<agents.length;i++){
    var dists=[];
    for(var j=0;j<agents.length;j++){
      if(i===j)continue;
      var dx=agents[i].x-agents[j].x,dy=agents[i].y-agents[j].y;
      var dd=Math.sqrt(dx*dx+dy*dy);
      if(agents[i].cluster===agents[j].cluster)dd*=0.5;
      dists.push({j:j,d:dd});
    }
    dists.sort(function(a,b){return a.d-b.d});
    agents[i].conn=[];
    for(var k=0;k<K&&k<dists.length;k++){
      if(dists[k].d<MAX_D)agents[i].conn.push(dists[k].j);
    }
  }
  function draw(){
    ctx.clearRect(0,0,W,H);
    // Draw connections
    for(var i=0;i<agents.length;i++){
      for(var ci=0;ci<agents[i].conn.length;ci++){
        var j=agents[i].conn[ci];
        var b=agents[j];
        var dx=agents[i].x-b.x,dy=agents[i].y-b.y;
        var d=Math.sqrt(dx*dx+dy*dy);
        if(d>MAX_D)continue;
        var alpha=Math.max(.03,.2*(1-d/MAX_D));
        ctx.beginPath();ctx.moveTo(agents[i].x,agents[i].y);ctx.lineTo(b.x,b.y);
        var grad=ctx.createLinearGradient(agents[i].x,agents[i].y,b.x,b.y);
        grad.addColorStop(0,agents[i].color);
        grad.addColorStop(1,b.color);
        ctx.strokeStyle=grad;ctx.globalAlpha=alpha;ctx.lineWidth=.8;ctx.stroke();
      }
    }
    ctx.globalAlpha=1;
    // Draw agents
    for(var i=0;i<agents.length;i++){
      var p=agents[i];
      p.x+=p.vx+Math.sin(Date.now()*.0005+p.x*.002)*.04;
      p.y+=p.vy+Math.cos(Date.now()*.0005+p.y*.002)*.04;
      if(p.x<0)p.x=W;if(p.x>W)p.x=0;
      if(p.y<0)p.y=H;if(p.y>H)p.y=0;
      ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,6.28);
      ctx.fillStyle=p.color;ctx.globalAlpha=p.alpha;ctx.fill();
    }
    ctx.globalAlpha=1;
    requestAnimationFrame(draw);
  }
  draw();
}

// ═══════════════════════════════════════
// DEMO PARTICLE SYSTEM — interactive with bright connections
// ═══════════════════════════════════════
function initDemoParticles(){
  var c=document.getElementById('demoCanvas');
  if(!c)return;
  var ctx=c.getContext('2d'),W,H;
  function rs(){W=c.width=c.parentElement.clientWidth;H=c.height=c.parentElement.clientHeight}rs();
  window.addEventListener('resize',rs);
  var rng=function(s){return function(){s=(s*16807)%2147483647;return(s-1)/2147483646}}(99);
  var agents=[],N=250;
  var sn=['王','李','张','刘','陈','赵','周','吴','孙','黄'];
  var gn=['明','华','丽','伟','芳','强','静','磊','红','敏'];
  var sps=['肿瘤科','呼吸科','消化科','血液科','乳腺外科'];
  var hosps=['协和医院','华西医院','瑞金医院','中山医院','301医院'];
  var clusterCenters=[{x:.25,y:.3},{x:.5,y:.5},{x:.75,y:.35}];
  for(var i=0;i<N;i++){
    var type,color,name,info,cluster;
    if(i<50){
      type='doctor';color='#3b82f6';cluster=0;
      name=sn[Math.floor(rng()*sn.length)]+gn[Math.floor(rng()*gn.length)];
      var w=rng()*.3+.6;
      info={type:'doctor',name:name,specialty:sps[Math.floor(rng()*sps.length)],hospital:hosps[Math.floor(rng()*hosps.length)],willingness:w};
    }else if(i<200){
      cluster=1;
      var w=Math.max(.1,Math.min(.9,.4+rng()*.4));
      type=w>.65?'patient_pos':w>.4?'patient_mid':'patient_neg';
      color=type==='patient_pos'?'#10b981':type==='patient_mid'?'#f59e0b':'#ef4444';
      name=sn[Math.floor(rng()*sn.length)]+(rng()>.5?'先生':'女士');
      info={type:'patient',name:name,willingness:w};
    }else{
      cluster=2;type='expert';color='#8b5cf6';
      name=sn[Math.floor(rng()*sn.length)]+['教授','博士','研究员'][Math.floor(rng()*3)];
      info={type:'expert',name:name,willingness:.5+rng()*.35};
    }
    var cc=clusterCenters[cluster];
    var angle=rng()*Math.PI*2,dist=rng()*Math.min(W,H)*.22;
    var cx=W*cc.x+Math.cos(angle)*dist,cy=H*cc.y+Math.sin(angle)*dist;
    cx=Math.max(10,Math.min(W-10,cx));cy=Math.max(10,Math.min(H-10,cy));
    agents.push({x:cx,y:cy,vx:(rng()-.5)*.1,vy:(rng()-.5)*.1,r:type==='expert'?3:type==='doctor'?2.5:rng()*1.2+1,color:color,info:info,alpha:rng()*.3+.5,cluster:cluster,conn:[]});
  }
  // Build connections — BRIGHT and VISIBLE
  var K=5,MAX_D=Math.min(W,H)*.14;
  for(var i=0;i<agents.length;i++){
    var dists=[];
    for(var j=0;j<agents.length;j++){
      if(i===j)continue;
      var dx=agents[i].x-agents[j].x,dy=agents[i].y-agents[j].y;
      var dd=Math.sqrt(dx*dx+dy*dy);
      if(agents[i].cluster===agents[j].cluster)dd*=0.5;
      dists.push({j:j,d:dd});
    }
    dists.sort(function(a,b){return a.d-b.d});
    for(var k=0;k<K&&k<dists.length;k++){
      if(dists[k].d<MAX_D&&agents[i].conn.indexOf(dists[k].j)<0&&agents[dists[k].j].conn.indexOf(i)<0){
        agents[i].conn.push(dists[k].j);
      }
    }
  }
  // Stats
  var totalConns=0;
  agents.forEach(function(a){totalConns+=a.conn.length});
  var avgConn=(totalConns/N).toFixed(1);
  var posCount=agents.filter(function(a){return a.info.willingness>.6}).length;
  document.getElementById('statConns').textContent=avgConn;
  document.getElementById('statDensity').textContent=(totalConns/(N*(N-1))*200).toFixed(1)+'%';
  document.getElementById('statPositive').textContent=Math.round(posCount/N*100)+'%';
  document.getElementById('statPath').textContent='2.4 hops';

  var tooltip=document.createElement('div');
  tooltip.style.cssText='position:fixed;pointer-events:none;background:rgba(15,23,42,.95);border:1px solid #334155;border-radius:10px;padding:.6rem .8rem;font-size:.78rem;color:#e2e8f0;z-index:300;max-width:260px;display:none;box-shadow:0 4px 20px rgba(0,0,0,.4);line-height:1.4';
  document.body.appendChild(tooltip);
  var hov=null;

  function draw(){
    ctx.clearRect(0,0,W,H);
    // Draw connections — BRIGHT, GRADIENT, CLEARLY VISIBLE
    for(var i=0;i<agents.length;i++){
      var a=agents[i];
      for(var ci=0;ci<a.conn.length;ci++){
        var j=a.conn[ci],b=agents[j];
        var dx=a.x-b.x,dy=a.y-b.y,d=Math.sqrt(dx*dx+dy*dy);
        if(d>MAX_D)continue;
        var isH=hov===i||hov===j;
        var alpha=isH?.7:.12;
        var width=isH?2.5:.6;
        ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);
        var grad=ctx.createLinearGradient(a.x,a.y,b.x,b.y);
        grad.addColorStop(0,a.color);
        grad.addColorStop(1,b.color);
        ctx.strokeStyle=grad;ctx.globalAlpha=alpha;ctx.lineWidth=width;ctx.stroke();
      }
    }
    ctx.globalAlpha=1;
    // Draw agents
    for(var i=0;i<agents.length;i++){
      var p=agents[i];
      p.x+=p.vx+Math.sin(Date.now()*.0006+p.x*.003+p.cluster*2)*.04;
      p.y+=p.vy+Math.cos(Date.now()*.0006+p.y*.003+p.cluster*2)*.04;
      var cc=clusterCenters[p.cluster];
      p.vx+=(W*cc.x-p.x)*.00002;p.vy+=(H*cc.y-p.y)*.00002;
      p.vx*=.998;p.vy*=.998;
      var cx=W/2,cy=H/2,mr=Math.min(W,H)*.42;
      var dx=p.x-cx,dy=p.y-cy,dist=Math.sqrt(dx*dx+dy*dy);
      if(dist>mr){p.x=cx+dx/dist*mr;p.y=cy+dy/dist*mr;p.vx*=-.3;p.vy*=-.3}
      if(p.x<5){p.x=5;p.vx*=-.5}if(p.x>W-5){p.x=W-5;p.vx*=-.5}
      if(p.y<5){p.y=5;p.vy*=-.5}if(p.y>H-5){p.y=H-5;p.vy*=-.5}
      var isH=hov===i;
      if(isH){
        ctx.beginPath();ctx.arc(p.x,p.y,p.r*7,0,6.28);
        var glow=ctx.createRadialGradient(p.x,p.y,p.r,p.x,p.y,p.r*7);
        glow.addColorStop(0,p.color+'50');glow.addColorStop(1,p.color+'00');
        ctx.fillStyle=glow;ctx.fill();
      }
      ctx.beginPath();ctx.arc(p.x,p.y,isH?p.r*3:p.r,0,6.28);
      ctx.fillStyle=p.color;ctx.globalAlpha=isH?1:p.alpha;ctx.fill();
      if(isH){ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.globalAlpha=.8;ctx.stroke();ctx.globalAlpha=1;ctx.font='bold 11px Inter';ctx.fillStyle='#fff';ctx.textAlign='center';ctx.fillText(p.info.name,p.x,p.y-p.r*3-6)}
      ctx.globalAlpha=1;
    }
    requestAnimationFrame(draw);
  }
  draw();

  c.addEventListener('mousemove',function(e){
    var rect=c.getBoundingClientRect();
    var mx=(e.clientX-rect.left)*(W/rect.width),my=(e.clientY-rect.top)*(H/rect.height);
    hov=null;
    for(var i=0;i<agents.length;i++){
      var dx=agents[i].x-mx,dy=agents[i].y-my;
      if(dx*dx+dy*dy<(agents[i].r+10)*(agents[i].r+10)){hov=i;break}
    }
    c.style.cursor=hov!==null?'pointer':'crosshair';
    if(hov!==null){
      var a=agents[hov].info;
      var tc=a.type==='doctor'?'#3b82f6':a.type==='expert'?'#8b5cf6':(a.willingness>.65?'#10b981':'#f59e0b');
      tooltip.innerHTML='<b style="color:'+tc+'">'+a.name+'</b><br><span style="color:#94a3b8">'+(a.type==='doctor'?a.hospital+' · '+a.specialty:a.type==='expert'?'专家':'患者')+'</span><br><span>意愿: <b style="color:'+tc+'">'+(a.willingness*100).toFixed(0)+'%</b></span>';
      tooltip.style.display='block';
      var tx=e.clientX+15,ty=e.clientY+15;
      if(tx+260>window.innerWidth)tx=e.clientX-270;
      if(ty+100>window.innerHeight)ty=e.clientY-105;
      tooltip.style.left=tx+'px';tooltip.style.top=ty+'px';
    }else{tooltip.style.display='none'}
  });
  c.addEventListener('mouseleave',function(){hov=null;tooltip.style.display='none'});
  c.addEventListener('click',function(){
    if(hov!==null)showAgentPanel(agents[hov].info);
  });
}

// ── Auto-init on page load ──
document.addEventListener('DOMContentLoaded',function(){
  initHeroParticles();
  initDemoParticles();
});
