"""v10 layout QA: all pages × 8 widths × 10 themes, overflow + element overlap, controls expanded.
Intended floating overlays (#navc, tile picker, theme pop, side drawer, topbar, toast, player) are recorded but not counted as failures.
"""
import asyncio,sys,json,os,time
from playwright.async_api import async_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8780/'
if not BASE.endswith('/'): BASE+='/'
pages=['maps.html','geo-bible.html','marks.html','index.html','bible.html','history.html','lorddays.html','compare.html','memory.html','sources.html','search.html','changelog.html','texts/index.html','texts/hc.html','texts/hc-1.html','texts/hc-2.html','texts/hc-3.html','texts/hc-4.html','texts/hc-5.html','texts/hc-all.html','texts/bc.html','texts/cd.html','texts/creeds.html']+[f'ld/{n:02d}.html' for n in range(1,53)]
if os.environ.get('PAGES'): pages=os.environ['PAGES'].split(',')
widths=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else [360,375,414,768,1024,1280,1440,1920]
THEMES=os.environ.get('THEMES', sys.argv[3] if len(sys.argv)>3 else 'night,dawn,forest,grape,ocean,sakura,citrus,ember,aurora,sumi').split(',')
OUT=os.environ.get('OUT','layout_v10_result.json')
Q=os.environ.get('Q','?cv0&nosw&maptest=local')
EXPAND='''()=>{
  document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));
  document.querySelectorAll('details').forEach(d=>d.open=true);
  document.querySelectorAll('section.sec').forEach(s=>s.style.contentVisibility='visible');
  const nav=document.getElementById('navc'); if(nav) nav.classList.add('open');
  const thp=document.getElementById('thp'); if(thp) thp.classList.add('open');
  document.querySelectorAll('.lmsrc').forEach((s,i)=>{if(i===0)s.classList.add('open')});
  document.querySelectorAll('.mklgd, details.mklgd, .legend details, details.legend').forEach(d=>d.open=true);
}'''
CLICK='''()=>{
  const vis=el=>{const r=el.getBoundingClientRect(),cs=getComputedStyle(el);return r.width&&r.height&&cs.display!=='none'&&cs.visibility!=='hidden'};
  document.querySelectorAll('details > summary').forEach(s=>{try{if(vis(s)&&!s.parentElement.open)s.click()}catch(e){}});
  const nav=document.querySelector('#navc .nv-tg, #navc button');
  if(nav&&vis(nav)&&!document.getElementById('navc').classList.contains('open')){try{nav.click()}catch(e){}}
  const ms=document.querySelector('.lmsrc > .lb[data-ms], .lmsrc > button');
  if(ms&&vis(ms)&&!document.querySelector('.lmsrc.open')){try{ms.click()}catch(e){}}
  const thb=document.querySelector('#thp > button');
  if(thb&&vis(thb)&&!document.getElementById('thp')?.classList.contains('open')){try{thb.click()}catch(e){}}
}'''
JS='''()=>{
const W=document.documentElement.clientWidth,H=innerHeight;
const res={sw:document.documentElement.scrollWidth,W,off:[],ov:[],hit:[],intended:[]};
const skipOv='.tbl,.mm,.mermaid,.mermaid-static,.leaflet-container,.lmap,.stops,.nav,.fc,svg,.lmspop,#thp,.thpop';
for(const el of document.querySelectorAll('main *')){
  if(el.closest(skipOv))continue;
  const r=el.getBoundingClientRect();if(r.width===0||r.height===0)continue;
  if(r.right>W+1||r.left<-1){const cs=getComputedStyle(el);if(cs.position==='fixed'||cs.position==='sticky')continue;res.off.push((el.className||el.tagName)+' '+Math.round(r.left)+'-'+Math.round(r.right));if(res.off.length>8)break}}
for(const el of document.querySelectorAll('.card,.qa,.art,.chip,.btn,.node,.ld')){
  if(el.scrollWidth>el.clientWidth+2&&getComputedStyle(el).overflowX!=='auto'&&getComputedStyle(el).overflowX!=='scroll'){res.ov.push((el.className)+':'+el.scrollWidth+'>'+el.clientWidth);if(res.ov.length>6)break}}
for(const el of document.querySelectorAll('.topbar > *, .nav a')){
  const r=el.getBoundingClientRect();if(r.width&&(r.right>W+1||r.left<-1))res.off.push('TOPBAR '+(el.className||el.tagName)+' '+Math.round(r.left)+'-'+Math.round(r.right))}
const box=el=>{const r=el.getBoundingClientRect(),cs=getComputedStyle(el);if(cs.display==='none'||cs.visibility==='hidden'||r.width<10||r.height<10||cs.opacity==='0')return null;return {el,r,pos:cs.position}};
const floating=[];
for(const sel of ['.topbar','#navc','#scrshield','.fab','#thp.open','.lmsrc.open .lmspop','.thpop','.toast','#player','.kbhelp','body.toc-open .side','body.toc-open .backdrop']){
  document.querySelectorAll(sel).forEach(el=>{const b=box(el);if(b)floating.push(b)})}
const content=[];
for(const sel of ['main h2','main .card','main .lmbar','main .qa','footer.foot','.mcard figcaption']){
  document.querySelectorAll(sel).forEach(el=>{const b=box(el);if(b)content.push(b)})}
const seen=new Set();
const isIntended=a=>{
  const id=a.el.id||''; const cls=(a.el.className||'').toString();
  return id==='navc'||id==='thp'||id==='scrshield'||id==='player'||cls.includes('fab')||cls.includes('lmspop')||cls.includes('thpop')||cls.includes('topbar')||cls.includes('toast')||cls.includes('kbhelp')||cls.includes('side')||cls.includes('backdrop');
};
for(const a of floating){
  if(a.el.id==='scrshield')continue;
  for(const b of content){
    if(a.el.contains(b.el)||b.el.contains(a.el))continue;
    const A=a.r,B=b.r;const ix=Math.max(0,Math.min(A.right,B.right)-Math.max(A.left,B.left));const iy=Math.max(0,Math.min(A.bottom,B.bottom)-Math.max(A.top,B.top));
    if(ix>12&&iy>12){
      const key=((a.el.id||a.el.className)+'' ).toString().slice(0,30)+' ∩ '+((b.el.id||b.el.className)+'').toString().slice(0,30)+' '+Math.round(ix)+'x'+Math.round(iy);
      const k=key+Math.round(A.top)+Math.round(B.top);if(seen.has(k))continue;seen.add(k);
      (isIntended(a)?res.intended:res.hit).push(key);
      if(res.hit.length>8)return res;
    }
  }
}
return res}'''

async def main():
    real=0; intended_n=0; checks=0
    findings=[]
    t0=time.time()
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for th in THEMES:
            for w in widths:
                ctx=await b.new_context(viewport={'width':w,'height':900},device_scale_factor=1)
                await ctx.add_init_script("localStorage.setItem('hc-theme',JSON.stringify(%s))" % json.dumps(th))
                pg=await ctx.new_page()
                for u in pages:
                    checks+=1
                    try:
                        await pg.goto(BASE+u+Q,wait_until='domcontentloaded',timeout=60000)
                        await pg.evaluate(EXPAND)
                        await pg.evaluate(CLICK)
                        await pg.evaluate("window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'})")
                        await pg.wait_for_timeout(80)
                        await pg.evaluate("window.scrollTo({top:0,behavior:'instant'})")
                        await pg.wait_for_timeout(40)
                        r=await pg.evaluate(JS)
                    except Exception as e:
                        real+=1; rec={'w':w,'th':th,'u':u,'error':str(e)[:200]}; findings.append(rec); print('ERR',w,th,u,e,flush=True); continue
                    overflow=r['sw']>r['W'] or r['off'] or r['ov']
                    if r.get('intended'): intended_n+=1
                    if overflow or r['hit']:
                        real+=1
                        rec={'w':w,'th':th,'u':u,'sw':r['sw'],'W':r['W'],'off':r['off'],'ov':r['ov'],'hit':r['hit']}
                        findings.append(rec)
                        print(w,th,u,json.dumps(rec,ensure_ascii=False)[:500],flush=True)
                await ctx.close()
                print('done',th,w,'checks',checks,'real',real,'elapsed',int(time.time()-t0),'s',flush=True)
        await b.close()
    out={'checks':checks,'pages':len(pages),'widths':widths,'themes':THEMES,'real_issues':real,'pages_with_intended_overlays':intended_n,'findings':findings,'seconds':round(time.time()-t0)}
    json.dump(out,open(OUT,'w'),ensure_ascii=False,indent=1)
    print('RESULT checks',checks,'real_issues',real,'intended_pages',intended_n,'wrote',OUT)

asyncio.run(main())
