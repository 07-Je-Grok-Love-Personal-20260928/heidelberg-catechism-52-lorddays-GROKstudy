"""v11 layout QA: v10.1 reduced theme matrix + TOC min/max widths.
All pages × 8 widths × night+dawn at default TOC; 10 heavy pages × remaining 8 themes × 8 widths;
plus all pages × 8 widths × night at TOC 220px and at max (60vw / 92vw), TOC fully expanded.
Intended floating overlays are recorded but not counted as failures.
"""
import asyncio,sys,json,os,time
from playwright.async_api import async_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8780/'
if not BASE.endswith('/'): BASE+='/'
ALL=['maps.html','geo-bible.html','marks.html','index.html','bible.html','history.html','lorddays.html','compare.html','memory.html','sources.html','search.html','changelog.html','texts/index.html','texts/hc.html','texts/hc-1.html','texts/hc-2.html','texts/hc-3.html','texts/hc-4.html','texts/hc-5.html','texts/hc-all.html','texts/bc.html','texts/cd.html','texts/creeds.html']+[f'ld/{n:02d}.html' for n in range(1,53)]
HEAVY=os.environ.get('HEAVY','maps.html,geo-bible.html,history.html,lorddays.html,memory.html,texts/hc-all.html,compare.html,texts/bc.html,texts/cd.html,index.html').split(',')
widths=[int(x) for x in (sys.argv[2].split(',') if len(sys.argv)>2 else '360,375,414,768,1024,1280,1440,1920').split(',') if x]
OUT=os.environ.get('OUT','/workspace/hc52-20261020/build/layout_v11_result.json')
Q=os.environ.get('Q','?cv0&nosw&maptest=local')
REST=['forest','grape','ocean','sakura','citrus','ember','aurora','sumi']

# reuse measure JS from layout_v10
import pathlib
src=pathlib.Path(__file__).with_name('layout_v10.py').read_text()
# extract EXPAND, CLICK, JS string constants
ns={}
exec(src.split('async def main')[0], ns)
EXPAND=ns['EXPAND']
CLICK=ns['CLICK']
JS=ns['JS']
TOC_EXPAND='''()=>{
  document.getElementById('tocExpand')?.click();
  document.querySelectorAll('#toc li.closed').forEach(li=>li.classList.remove('closed'));
  if (matchMedia('(max-width:1024px)').matches) document.body.classList.add('toc-open');
  else document.body.classList.remove('toc-hidden');
}'''
SET_SIDE='''(w)=>{
  const MIN=220, maxW=Math.max(MIN,Math.round(innerWidth*(matchMedia('(max-width:1024px)').matches?0.92:0.6)));
  const n=(w==='max'||w==='9999')?maxW:Math.max(MIN,Math.min(maxW,Math.round(+w||300)));
  document.documentElement.style.setProperty('--side',n+'px');
  try{localStorage.setItem('hc-side-w',JSON.stringify(n))}catch(e){}
  return n;
}'''

async def run_batch(b, pages, themes, widths, side, findings):
    real=0; intended_n=0; checks=0
    for th in themes:
        for w in widths:
            ctx=await b.new_context(viewport={'width':w,'height':900},device_scale_factor=1)
            await ctx.add_init_script("localStorage.setItem('hc-theme',JSON.stringify(%s))" % json.dumps(th))
            if side=='min':
                await ctx.add_init_script("localStorage.setItem('hc-side-w',JSON.stringify(220))")
            elif side=='max':
                # large value; app.js clamps to maxW() on load
                await ctx.add_init_script("localStorage.setItem('hc-side-w',JSON.stringify(9999))")
            pg=await ctx.new_page()
            for u in pages:
                checks+=1
                try:
                    await pg.goto(BASE+u+Q,wait_until='domcontentloaded',timeout=60000)
                    await pg.evaluate(EXPAND)
                    await pg.evaluate(CLICK)
                    await pg.evaluate(TOC_EXPAND)
                    if side=='min': await pg.evaluate(SET_SIDE, 220)
                    elif side=='max': await pg.evaluate(SET_SIDE, 'max')
                    await pg.evaluate("window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'})")
                    await pg.wait_for_timeout(60)
                    await pg.evaluate("window.scrollTo({top:0,behavior:'instant'})")
                    await pg.wait_for_timeout(30)
                    r=await pg.evaluate(JS)
                    if side!='default':
                        r['side']=await pg.evaluate("()=>getComputedStyle(document.documentElement).getPropertyValue('--side').trim()")
                except Exception as e:
                    real+=1; rec={'w':w,'th':th,'u':u,'side':side,'error':str(e)[:200]}; findings.append(rec); print('ERR',side,w,th,u,e,flush=True); continue
                overflow=r['sw']>r['W'] or r['off'] or r['ov']
                if r.get('intended'): intended_n+=1
                if overflow or r['hit']:
                    real+=1
                    rec={'w':w,'th':th,'u':u,'side':side,'sw':r['sw'],'W':r['W'],'off':r['off'],'ov':r['ov'],'hit':r['hit'],'sideW':r.get('side')}
                    findings.append(rec)
                    print(side,w,th,u,json.dumps(rec,ensure_ascii=False)[:500],flush=True)
            await ctx.close()
            print('done',side,th,w,'checks',checks,'real',real,flush=True)
    return checks,real,intended_n

async def main():
    findings=[]; t0=time.time()
    checks=real=intended_n=0
    batches=[]
    async with async_playwright() as p:
        b=await p.chromium.launch()
        # A: all pages × 8 widths × night+dawn, default TOC (expanded)
        c,r,i=await run_batch(b, ALL, ['night','dawn'], widths, 'default', findings)
        checks+=c; real+=r; intended_n+=i
        # B: 10 heavy × remaining 8 themes × 8 widths, default TOC
        c,r,i=await run_batch(b, HEAVY, REST, widths, 'default', findings)
        checks+=c; real+=r; intended_n+=i
        # C: TOC min + max, all pages × 8 widths × night
        for side in ('min','max'):
            c,r,i=await run_batch(b, ALL, ['night'], widths, side, findings)
            checks+=c; real+=r; intended_n+=i
        await b.close()
    out={'checks':checks,'pages':len(ALL),'heavy':HEAVY,'widths':widths,'real_issues':real,'pages_with_intended_overlays':intended_n,'findings':findings,'seconds':round(time.time()-t0)}
    json.dump(out,open(OUT,'w'),ensure_ascii=False,indent=1)
    print('RESULT checks',checks,'real_issues',real,'intended_pages',intended_n,'secs',out['seconds'],'wrote',OUT)

asyncio.run(main())
