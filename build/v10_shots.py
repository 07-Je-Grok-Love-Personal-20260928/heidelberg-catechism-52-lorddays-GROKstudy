"""v10 screenshots → shots/."""
import asyncio,sys,os
from playwright.async_api import async_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8780/'
OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(os.path.dirname(__file__),'..','shots')
TH=['night','dawn','forest','grape','ocean','sakura','citrus','ember','aurora','sumi']
async def shot(pg,url,theme,path,sel=None,pre=None,wait=1200):
    await pg.goto(BASE+url+('&' if '?' in url else '?')+'nosw',wait_until='domcontentloaded')
    await pg.evaluate(f"localStorage.setItem('hc-theme',JSON.stringify('{theme}'))")
    await pg.reload(wait_until='load');await pg.wait_for_timeout(wait)
    if pre: await pg.evaluate(pre);await pg.wait_for_timeout(800)
    await pg.add_style_tag(content='.fab,#navc,.progress{visibility:hidden!important}')
    if sel:
        el=pg.locator(sel).first;await el.scroll_into_view_if_needed();await pg.wait_for_timeout(1500);await el.screenshot(path=path)
    else:
        await pg.screenshot(path=path)
    print('saved',path,flush=True)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        c=await b.new_context(viewport={'width':1440,'height':900});pg=await c.new_page()
        for t in TH: await shot(pg,'index.html',t,f'{OUT}/v10-theme-{t}.png')
        await shot(pg,'index.html','sakura',f'{OUT}/v10-theme-picker.png',pre="document.getElementById('thp').classList.add('open')")
        await shot(pg,'ld/01.html','sumi',f'{OUT}/v10-marks-review-sumi.png',pre="document.documentElement.classList.add('mkrev')",sel='section:has(#essence)')
        await shot(pg,'marks.html','citrus',f'{OUT}/v10-marks-legend-citrus.png',sel='main section.sec')
        await shot(pg,'maps.html?maptest=local','ember',f'{OUT}/v10-scene-heidelberg-ember.png',sel='section:has(#m-hd1563)')
        await shot(pg,'maps.html?maptest=local','dawn',f'{OUT}/v10-explainer-tyw-dawn.png',sel='section:has(#m-tyw)')
        await shot(pg,'maps.html?maptest=local','ocean',f'{OUT}/v10-map-trans-ocean.png',sel='section:has(#m-trans)')
        await shot(pg,'maps.html?maptest=local','aurora',f'{OUT}/v10-map-today-aurora.png',sel='section:has(#m-today)')
        await shot(pg,'geo-bible.html?maptest=local','forest',f'{OUT}/v10-geo-gal-forest.png',sel='section:has(#m-gal)')
        await shot(pg,'maps.html?maptest=local','night',f'{OUT}/v10-tile-picker.png',pre="document.querySelector('.lmsrc')?.classList.add('open')",sel='section:has(#m-ref) .mpair, section:has(#m-ref)')
        m=await b.new_context(viewport={'width':375,'height':812},device_scale_factor=2,is_mobile=True,has_touch=True);mp=await m.new_page()
        await shot(mp,'ld/01.html','sakura',f'{OUT}/v10-mobile-ld01-sakura.png')
        await shot(mp,'maps.html?maptest=local','citrus',f'{OUT}/v10-mobile-maps-citrus.png')
        await b.close()
asyncio.run(main())
