/* PharmaSim Shared Navigation Component v1.0 */
(function(){
  var pages = [
    {href:'index.html',label:'Home'},
    {href:'dashboard.html',label:'Dashboard'},
    {href:'pipeline.html',label:'Pipeline'},
    {href:'calculator.html',label:'Calculator'},
    {href:'compare.html',label:'Compare'},
    {href:'demo.html',label:'Demo'},
    {href:'api.html',label:'API'},
    {href:'about.html',label:'About'},
    {href:'pricing.html',label:'Pricing'},
    {href:'contact.html',label:'Contact'}
  ];
  
  var current = location.pathname.split('/').pop() || 'index.html';
  
  // Remove all existing navs to avoid duplicates
  var existingNavs = document.querySelectorAll('nav, #opc-nav');
  existingNavs.forEach(function(n){ 
    if (n.id !== 'pharmasim-nav') n.remove(); 
  });
  
  var nav = document.createElement('nav');
  nav.id = 'pharmasim-nav';
  nav.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:rgba(8,12,24,.95);backdrop-filter:blur(16px);border-bottom:1px solid rgba(30,41,59,.5);padding:0 1.5rem;height:54px;display:flex;align-items:center;justify-content:space-between;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif';
  
  var brand = document.createElement('a');
  brand.href = 'index.html';
  brand.style.cssText = 'display:flex;align-items:center;gap:8px;text-decoration:none;font-weight:800;font-size:15px;color:#f1f5f9';
  brand.innerHTML = '<svg width="24" height="24" viewBox="0 0 28 28" fill="none"><rect x="2" y="2" width="24" height="24" rx="6" fill="url(#sng1)"/><path d="M9 10h10M9 14h10M9 18h6" stroke="#fff" stroke-width="2" stroke-linecap="round"/><defs><linearGradient id="sng1" x1="2" y1="2" x2="26" y2="26"><stop stop-color="#06b6d4"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs></svg><span style="background:linear-gradient(135deg,#06b6d4,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent">PharmaSim</span>';
  nav.appendChild(brand);
  
  var links = document.createElement('div');
  links.style.cssText = 'display:flex;gap:2px;align-items:center;overflow-x:auto';
  pages.forEach(function(p){
    var a = document.createElement('a');
    a.href = p.href;
    a.textContent = p.label;
    var isActive = current === p.href;
    a.style.cssText = 'padding:6px 12px;border-radius:7px;font-size:13px;font-weight:500;text-decoration:none;white-space:nowrap;transition:all .2s;color:' + (isActive?'#06b6d4':'rgba(255,255,255,.6)') + ';background:' + (isActive?'rgba(6,182,212,.1)':'transparent');
    a.onmouseenter = function(){if(!isActive){this.style.color='#fff';this.style.background='rgba(255,255,255,.04)'}};
    a.onmouseleave = function(){if(!isActive){this.style.color='rgba(255,255,255,.6)';this.style.background='transparent'}};
    links.appendChild(a);
  });
  nav.appendChild(links);
  
  var eco = document.createElement('a');
  eco.href = 'https://mokangmedical.github.io/opc-homepage/';
  eco.textContent = 'OPC Ecosystem';
  eco.style.cssText = 'padding:5px 14px;border-radius:7px;font-size:12px;font-weight:600;text-decoration:none;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;white-space:nowrap';
  nav.appendChild(eco);
  
  document.body.insertBefore(nav, document.body.firstChild);
  document.body.style.paddingTop = '70px';
})();