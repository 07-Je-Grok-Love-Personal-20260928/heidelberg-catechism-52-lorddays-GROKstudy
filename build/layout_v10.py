"""v10 layout QA: 8 widths × theme, overflow + element overlap, controls expanded."""
import asyncio,sys,json,os
from playwright.async_api import async_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8780/'
pages=['maps.html','geo-bible.html','marks.html','index.html','bible.html','history.html','lorddays.html','compare.html','memory.html','sources.html','search.html','changelog.html','texts/index.html','texts/hc.html','texts/hc-1.html','texts/hc-2.html','texts/hc-3.html','texts/hc-4.html','texts/hc-5.html','texts/hc-all.html','texts/bc.html','texts/cd.html','texts/creeds.html']+[f'ld/{n:02d}.html' for n in range(1,53)]
if os.environ.get('PAGES'): pages=os.environ['PAGES'].split(',')
widths=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else [360,375,414,768,1024,1280,1440,1920]
TH=sys.argv[3] if len(sys.argv)>3 else None
EXPAND='''()=>{
  document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));
  document.querySelectorAll('details').forEach(d=>d.open=true);
  document.querySelectorAll('section.sec').forEach(s=>s.style.contentVisibility='visible');
  const nav=document.getElementById('navc'); if(nav) nav.classList.add('open');
  const thp=document.getElementById('thp'); if(thp) thp.classList.add('open');
  document.querySelectorAll('.lmsrc').forEach((s,i)=>{if(i===0)s.classList.add('open')});
  document.querySelectorAll('.mklgd, details.mklgd').forEach(d=>d.open=true);
}'''
JS='''()=>{const W=document.documentElement.clientWidth,H=innerHeight;const res={sw:document.documentElement.scrollWidth,W,off:[],ov:[],hit:[]};
for(const el of document.querySelectorAll('main *')){
  if(el.closest('.tbl,.mm,.mermaid,.leaflet-container,.lmap,.stops,.nav,.fc,svg,.lmspop,#thp'))continue;
  const r=el.getBoundingClientRect();if(r.width===0)continue;
  if(r.right>W+1||r.left<-1){const cs=getComputedStyle(el);if(cs.position==='fixed')continue;res.off.push((el.className||el.tagName)+' '+Math.round(r.left)+'-'+Math.round(r.right));if(res.off.length>8)break}}
for(const el of document.querySelectorAll('.card,.qa,.art,.chip,.btn,.node,.ld')){
  if(el.scrollWidth>el.clientWidth+2&&getComputedStyle(el).overflowX!=='auto'){res.ov.push((el.className)+':'+el.scrollWidth+'>'+el.clientWidth);if(res.ov.length>6)break}}
for(const el of document.querySelectorAll('.topbar > *, .nav a')){
  const r=el.getBoundingClientRect();if(r.width&&(r.right>W+1||r.left<-1))res.off.push('TOPBAR '+(el.className||el.tagName)+' '+Math.round(r.left)+'-'+Math.round(r.right))}
const box=el=>{const r=el.getBoundingClientRect(),cs=getComputedStyle(el);if(cs.display==='none'||cs.visibility==='hidden'||r.width<10||r.height<10||cs.opacity==='0')return null;return {el,r,pos:cs.position}};
const fixed=[];
for(const sel of ['.topbar','#navc','#scrshield','.fab','.side','#thp.open','.lmsrc.open .lmspop']){
  document.querySelectorAll(sel).forEach(el=>{const b=box(el);if(b)fixed.push(b)})}
const content=[];
for(const sel of ['main h2','main .card','main .lmbar','main .qa','footer.foot']){
  document.querySelectorAll(sel).forEach(el=>{const b=box(el);if(b)content.push(b)})}
const seen=new Set();
for(const a of fixed){
  if(a.el.id==='scrshield')continue;
  for(const b of content){
    if(a.el.contains(b.el)||b.el.contains(a.el))continue;
    const A=a.r,B=b.r;const ix=Math.max(0,Math.min(A.right,B.right)-Math.max(A.left,B.left));const iy=Math.max(0,Math.min(A.bottom,B.bottom)-Math.max(A.top,B.top));
    if(ix>12&&iy>12){const key=a.el.id||a.el.className;const k=key+'x'+(b.el.id||b.el.className)+Math.round(A.top)+Math.round(B.top);if(seen.has(k))continue;seen.add(k);
      res.hit.push(((a.el.id||a.el.className)+'' ).toString().slice(0,30)+' ∩ '+((b.el.id||b.el.className)+'').toString().slice(0,30)+' '+Math.round(ix)+'x'+Math.round(iy));if(res.hit.length>8)return res}}}
return res}'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        issues=0
        for w in widths:
            ctx=await b.new_context(viewport={'width':w,'height':900},device_scale_factor=1)
            pg=await ctx.new_page()
            if TH: await pg.add_init_script("localStorage.setItem('hc-theme',JSON.stringify('%s'))"%TH)
            for u in pages:
                await pg.goto(BASE+u+'?cv0&nosw',wait_until='load',timeout=60000)
                await pg.evaluate(EXPAND)
                await pg.evaluate("window.scrollTo({top:document.body.scrollHeight,behavior:'instant'})");await pg.wait_for_timeout(200)
                await pg.evaluate("window.scrollTo({top:0,behavior:'instant'})");await pg.wait_for_timeout(80)
                r=await pg.evaluate(JS)
                if r['sw']>r['W'] or r['off'] or r['ov'] or r['hit']:
                    issues+=1; print(w,u,json.dumps(r,ensure_ascii=False)[:700],flush=True)
            await ctx.close();print('width',w,'done',TH,flush=True)
        print('issues',issues)
        await b.close()
asyncio.run(main())
