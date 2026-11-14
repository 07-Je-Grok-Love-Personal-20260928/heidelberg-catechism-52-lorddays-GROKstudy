# v8 · 历史地图集 (maps.html) + 圣经地理 (geo-bible.html) + reusable map blocks for history.html and Lord's Day pages
from common import *
import maps_data as MD, mapsvg, shutil
BOOKS={'创':'创','出':'出','徒':'徒','林前':'林前'}
def ldlink(n,pre): return f'<a class="chip ldc" href="{pre}ld/{n:02d}.html">{esc(ld_label(n))}</a>'
def mapdef(m):
    pk={p[0]:p for p in m['places']}
    d=dict(id=m['id'],bbox=m['bbox'],world=bool(m.get('world')),
      places=[dict(k=p[0],n=p[1],en=p[2],c=[p[3],p[4]],y=p[5],d=p[6],cv=p[7],i=i+1,**({'era':p[9]} if len(p)>9 else {})) for i,p in enumerate(m['places'])],
      routes=[dict(k=r[0],t=r[1],cv=r[2],s=r[3],pts=[pk[k][0] for k in r[4]]) for r in m['routes']],
      regions=[dict(n=r[0],c=[r[1],r[2]],km=r[3],cv=r[4]) for r in m.get('regions',[])],
      world_pts=[dict(n=w[0],c=[w[1],w[2]],y=w[3],d=w[4]) for w in m.get('worldpts',[])])
    return f'<script type="application/json" id="md-{m["id"]}">{json.dumps(d,ensure_ascii=False,separators=(",",":"))}</script>'
def live_box(m,P=None):
    P=P or mapsvg.Proj(m['bbox'])
    lay='<div class="lmbar" role="group" aria-label="底图"><button type="button" class="lb on" data-ml="auto" title="自动：按列表探测可用底图，失败时依次回退">🗺️ 自动</button><div class="lmsrc"><button type="button" class="lb" data-ms aria-haspopup="listbox" aria-expanded="false" title="选择底图来源（自动记住）">📚 底图</button><div class="lmspop" role="listbox"></div></div><button type="button" class="lb" data-ml="sat" title="卫星影像（Esri World Imagery）">🛰️ 卫星</button><button type="button" class="lb" data-ml="local" title="站内自托管矢量底图：离线、全球可用">🎨 主题</button><button type="button" class="lb" data-mfit title="复位视野">🎯</button>'+('<button type="button" class="lb" data-mworld title="全球视野">🌍</button>' if m.get('world') else '')+'</div>'
    return (f'<div class="lmap" data-map="{m["id"]}" style="aspect-ratio:{P.W}/{P.H}"><div class="lm-fb" aria-hidden="true"><svg viewBox="0 0 {P.W} {P.H}" class="cmap fbk"><use href="#cmg-{m["id"]}"/></svg></div>'
            f'<div class="lm-in"></div><div class="lm-st" role="status">🗺️ 实时地图将在滚动到此处时加载…</div></div>{lay}')
def quote_html(m):
    return ''.join(f'<p class="vq">“<span class="mk-k">{esc(q)}</span>”（{b}{c}:{a}{"-"+str(z) if z!=a else ""}）</p>' for q,b,c,a,z in m.get('quotes',[]))
def map_section(m,pre='',num=None):
    P=mapsvg.Proj(m['bbox']); uid=m['id']
    rtl='<div class="rtl" role="group" aria-label="路线开关">'+''.join(f'<button type="button" class="rtb on" data-rt="{uid}:{r[0]}" style="--c:var({r[2]})" aria-pressed="true" title="{esc(r[5] or r[1])}"><i class="sw {r[3]}"></i>{esc(r[1])}</button>' for r in m['routes'])+(f'<button type="button" class="rtb play" data-play="{uid}">▶ 播放路线</button>' if len(m['routes'])<6 or uid=='dort' else '')+'</div>'
    stops='<ol class="stops">'+''.join(f'<li><button type="button" data-pk="{uid}:{p[0]}" style="--c:var({p[7]})"><b>{i+1}</b>{esc(p[1])}<small>{esc(p[5])}</small></button></li>' for i,p in enumerate(m['places']))+'</ol>'
    cap={'scene':'🎨 情景图','explainer':'🎨 讲解图','schematic':'🎨 示意图','concept':'🎨 概念示意图'}.get(m.get('art','schematic'),'🎨 概念示意图')
    pair=(f'<div class="mpair"><figure class="mcard cm reveal"><figcaption>{cap} <span class="small muted">· 动画 · 编号地点</span></figcaption>{mapsvg.illustrate(m)}</figure>'
          f'<figure class="mcard lv"><figcaption>🛰️ 实时交互地图 <span class="small muted">· 拖动 / 双指缩放 · 点击地点</span></figcaption>{live_box(m,P)}</figure></div>')
    story='<ol class="tlm">'+''.join(f'<li><span class="y">{esc(y)}</span><span>{md(t)}</span></li>' for y,t in m['story'])+'</ol>'
    tbl='<div class="tbl"><table><thead><tr><th>#</th><th>地点</th><th>年代</th><th>意义</th></tr></thead><tbody>'+''.join(f'<tr><td><b style="color:var({p[7]})">{i+1}</b></td><td><b>{esc(p[1])}</b><br><span class="small muted">{esc(p[2])}</span></td><td class="nw">{esc(p[5])}</td><td>{esc(p[6])}</td></tr>' for i,p in enumerate(m['places']))+'</tbody></table></div>'
    lds='<div class="ldlinks">'+''.join(f'<div class="ldl">{ldlink(n,pre)}<span class="small">{esc(w)}</span></div>' for n,w in m['lds'])+'</div>'
    extra=''
    if m.get('worldpts'): extra+=f'<div class="card reveal"><h3 id="{uid}-world">🌍 走向全球：移民与宣教</h3><div class="chart">{mapsvg.world_inset(m)}</div><p class="small muted">示意：从海德堡出发的线条只表示传播方向，不表示实际航线。</p></div>'
    if m.get('deleg'): extra+=f'<div class="card reveal"><h3 id="{uid}-bars">📊 外国代表团人数（共 27 人）</h3>{deleg_bars(m)}</div>'
    if uid=='ref': extra+=f'<div class="card reveal"><h3 id="ref-dots">📈 改教城市时间轴：一个世纪的接力</h3>{ref_dots(m)}</div>'
    if uid=='trans': extra+=f'<div class="card reveal"><h3 id="trans-bars">📊 主要译本与年份（示意）</h3>{trans_bars()}</div>'
    if uid=='today': extra+=f'<div class="card reveal"><h3 id="today-note">⚖️ 两个改革宗家庭</h3><p>{md("**欧陆改革宗**以三项联合信条为准则；**长老会改革宗**以威斯敏斯特准则为准则。二者同源（改革宗神学），文件与教会政治不同。本图标出的是仍认信或使用要理问答的若干地点，**不是世界改革宗的完整地图**。")}</p></div>'

    inner=(callout('core','本质',md(m['core']))+pair+rtl+stops+extra+
      f'<div class="grid g2"><div class="card pan why reveal"><h3 id="{uid}-why">🏛️ 为什么与要理问答有关</h3><p>{md(m["why"])}</p>{quote_html(m)}</div>'
      f'<div class="card pan cov reveal"><h3 id="{uid}-story">⏳ 时间线</h3>{story}</div></div>'
      f'<div class="grid g2"><div class="card pan app reveal"><h3 id="{uid}-cul">🏞️ 文化侧写</h3><ul class="clean">{"".join(f"<li>{md(x)}</li>" for x in m["culture"])}</ul></div>'
      f'<div class="card pan xref reveal"><h3 id="{uid}-ld">📅 相关主日</h3>{lds}</div></div>'
      f'<details class="card reveal ptbl"><summary><b>📋 地点一览（{len(m["places"])} 处 · 点击展开）</b></summary>{tbl}</details>'
      +callout('hook','记忆钩',f'<b style="font-family:var(--serif);font-size:1.1em">{esc(m["hook"])}</b>')+mapdef(m))
    return sec('m-'+uid,m['ico'],m['title'],inner,'msec')
def deleg_bars(m):
    rows=m['deleg']; mx=max(r[1] for r in rows); W=560; rh=28; H=len(rows)*rh+10
    o=[f'<svg class="bars" viewBox="0 0 {W} {H}" role="img" aria-label="多特大会外国代表团人数" style="width:100%;height:auto">']
    for i,(n,v,c) in enumerate(rows):
        y=i*rh+4; w=(W-200)*v/mx if v else 0
        o.append(f'<text x="118" y="{y+17}" text-anchor="end" style="fill:var(--fg);font-size:13px">{esc(n)}</text><rect class="bar-grow" x="126" y="{y+3}" width="{max(w,3):.0f}" height="18" rx="9" style="fill:var({c});--i:{i}"/><text x="{132+w:.0f}" y="{y+17}" style="fill:var(--fg);font-size:13px;font-weight:800">{v if v else "空位"}</text>')
    o.append('</svg>'); return ''.join(o)
def ref_dots(m):
    pts=[(1517,'维滕堡','--gold'),(1519,'苏黎世','--grat'),(1523,'斯特拉斯堡','--teal'),(1529,'巴塞尔','--teal'),(1529,'马尔堡','--misery'),(1536,'日内瓦','--grat'),(1550,'伦敦','--intro'),(1563,'海德堡','--deliv'),(1571,'埃姆登','--intro'),(1619,'多特','--grat')]
    # v9: four label tiers (2 above, 2 below the axis), greedy placement so dense years (1517–1536) never overlap
    W=640;H=196;AY=96;X=lambda y:30+(y-1510)*(W-60)/115
    TI=[(60,46,-1),(136,150,1),(28,14,-1),(170,184,1)]  # (name y, year y, side)
    o=[f'<svg class="dots" viewBox="0 0 {W} {H}" role="img" aria-label="改教城市时间轴" style="width:100%;height:auto"><line x1="30" x2="{W-30}" y1="{AY}" y2="{AY}" style="stroke:var(--bd);stroke-width:3"/>']
    for yv in range(1510,1630,20): o.append(f'<text x="{X(yv):.0f}" y="{AY+18}" text-anchor="middle" style="fill:var(--muted);font-size:10.5px">{yv}</text><line x1="{X(yv):.0f}" x2="{X(yv):.0f}" y1="{AY-6}" y2="{AY+6}" style="stroke:var(--bd)"/>')
    right=[-1e9]*4
    for i,(y,n,c) in enumerate(pts):
        x=X(y);hw=max(12.5*len(n),30)/2+4
        k=next((t for t in range(4) if right[t]<x-hw),min(range(4),key=lambda t:right[t]));right[k]=x+hw
        ny,yy,sd=TI[k];ly=ny+8 if sd<0 else ny-13
        o.append(f'<g class="dot" style="--i:{i}"><line x1="{x:.0f}" x2="{x:.0f}" y1="{AY}" y2="{ly}" style="stroke:var({c});stroke-dasharray:2 3"/><circle cx="{x:.0f}" cy="{AY}" r="7" style="fill:var({c})"/><text x="{x:.0f}" y="{ny}" text-anchor="middle" style="fill:var(--fg);font-size:12px;font-weight:800">{n}</text><text x="{x:.0f}" y="{yy}" text-anchor="middle" style="fill:var({c});font-size:11px;font-weight:700">{y}</text></g>')
    if right[3]<-1e8: o[0]=o[0].replace(f'viewBox="0 0 {W} {H}"',f'viewBox="0 0 {W} 160"')
    o.append('</svg>'); return ''.join(o)
def trans_bars():
    rows=[('德文 / 拉丁文','1563',100,'--deliv'),('荷兰文','1563–66',86,'--intro'),('英文','1567',70,'--gold'),('多特公订','1619',100,'--grat'),('随荷兰教会出海','十七世纪',78,'--teal'),('汉语等近现代译本','近现代',64,'--misery')]
    W=640; rh=30; H=len(rows)*rh+8
    o=[f'<svg class="bars" viewBox="0 0 {W} {H}" role="img" aria-label="主要译本与年份" style="width:100%;height:auto">']
    for i,(n,y,v,c) in enumerate(rows):
        yy=i*rh+4; w=(W-240)*v/100
        o.append(f'<text x="150" y="{yy+17}" text-anchor="end" style="fill:var(--fg);font-size:13px">{esc(n)}</text><rect class="bar-grow" x="158" y="{yy+4}" width="{w:.0f}" height="18" rx="9" style="fill:var({c});--i:{i}"/><text x="{166+w:.0f}" y="{yy+17}" style="fill:var(--fg);font-size:12.5px;font-weight:700">{esc(y)}</text>')
    o.append('</svg><p class="small muted">长度只表示「这一步在传播史上的分量」的示意，不是印数或语种完备清单。</p>'); return ''.join(o)

def lanes_chart(maps):
    """Overview: one lane per map, year span of its story (history maps only)."""
    import re as _r
    W=640; rows=[m for m in maps if m['page']=='maps']; H=len(rows)*34+30; ysall=[int(x) for m in maps if m["page"]=="maps" for y,_ in m["story"] for x in _r.findall(r"1[4-9]\d\d",y)] or [1500,1650]; y0,y1=min(ysall)//25*25, (max(ysall)+24)//25*25; X=lambda y:110+(y-y0)*(W-130)/max(y1-y0,1)
    o=[f'<svg class="lanes" viewBox="0 0 {W} {H}" role="img" aria-label="历史地图的年代跨度" style="width:100%;min-width:520px;height:auto">']
    cols=['--deliv','--gold','--intro','--teal','--grat']
    for i,m in enumerate(rows):
        ys=[int(x) for y,_ in m['story'] for x in _r.findall(r'1[4-9]\d\d',y)]; a,b=(min(ys) if ys else y0),(max(ys) if ys else y1); y=i*34+6
        o.append(f'<a href="#m-{m["id"]}"><text x="102" y="{y+16}" text-anchor="end" style="fill:var(--fg);font-size:12.5px;font-weight:700">{m["ico"]} {esc(m["short"])}</text><rect class="bar-grow" x="{X(a):.0f}" y="{y+3}" width="{max(X(b)-X(a),8):.0f}" height="18" rx="9" style="fill:var({cols[i%5]});--i:{i}"/>'
                 +''.join(f'<circle cx="{X(int(t)):.0f}" cy="{y+12}" r="3.2" style="fill:var(--ink)"/>' for yy,_ in m['story'] for t in _r.findall(r'1[4-9]\d\d',yy)[:1] if int(t)>=y0)+'</a>')
    for yv in range(y0,y1+1,max(25,(y1-y0)//6 or 25)): o.append(f'<text x="{X(yv):.0f}" y="{H-4}" text-anchor="middle" style="fill:var(--muted);font-size:11px">{yv}</text>')
    o.append('</svg>'); return ''.join(o)
def atlas_cards(maps,pre=''):
    return '<div class="grid g4 atl">'+''.join(f'<a class="card lift atc" href="{pre}{"maps" if m["page"]=="maps" else "geo-bible"}.html#m-{m["id"]}" style="--c:var({m["places"][0][7]})"><span class="ai">{m["ico"]}</span><b>{esc(m["short"])}</b><span class="small muted">{len(m["places"])} 个地点 · {len(m["routes"])} 条路线</span></a>' for m in maps)+'</div>'
MAPJS=lambda pre:f'<script src="{pre}assets/js/map.js" defer data-root="{pre}"></script>'
SRCNOTE='<p class="small muted mapsrc">🧭 地图说明：示意图 / 情景图 / 讲解图与“主题”底图由 Natural Earth（公有领域）在本站构建时生成，<b>不依赖任何外部服务</b>。实时地图使用本站自带的 MapLibre GL 引擎。在线底图可在每张地图的「📚 底图」中手动选择（选择会自动记住），也可使用「🗺️ 自动」：按 Esri 街道 / 地形 / CARTO Voyager · Positron / OSM / OSM Humanitarian / OpenTopoMap / OpenFreeMap / Esri 国家地理 · 自然地貌 / USGS / GeoQ / 高德 的顺序探测，8 秒无瓦片或连续失败即改用下一个；全部失败则退回站内 Natural Earth 底图。卫星为 Esri World Imagery。Stadia / Stamen 现需密钥，本站未接入。高德与 GeoQ 为中国可达源，采用 GCJ-02 坐标，与本站 WGS-84 地点会有数百米偏移，仅作底图；高德无官方密钥，公开瓦片随时可能失效。浏览器不支持 WebGL 时显示同一幅示意图。历史区域圆圈仅为示意，不代表当时的精确疆界；圣经地点多为传统推测位置。</p>'
def build():
    os.makedirs(os.path.join(SITE,'assets','geo'),exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(__file__),'geo_out','base.json'),os.path.join(SITE,'assets','geo','base.json'))
    vd=os.path.join(SITE,'assets','vendor'); os.makedirs(vd,exist_ok=True)
    srcdir='/workspace/tools/node_modules/maplibre-gl/dist'
    if not os.path.exists(os.path.join(srcdir,'maplibre-gl.js')):
        srcdir=vd  # already in the site tree (e.g. after a box reset)
    for f in ('maplibre-gl.js','maplibre-gl.css','LICENSE.txt'):
        src=os.path.join(srcdir, f if f!='LICENSE.txt' or os.path.exists(os.path.join(srcdir,'LICENSE.txt')) else 'maplibre-LICENSE.txt')
        dst=os.path.join(vd,('maplibre-' if f=='LICENSE.txt' else '')+f)
        if os.path.abspath(src)!=os.path.abspath(dst) and os.path.exists(src):
            shutil.copy(src,dst)
    H=[m for m in MD.MAPS if m['page']=='maps']; B=[m for m in MD.MAPS if m['page']=='bible']
    npl=sum(len(m['places']) for m in H); nrt=sum(len(m['routes']) for m in H)
    kpi=''.join(f'<div><b>{v}</b>{t}</div>' for v,t in [(len(H),'张历史地图'),(npl,'个地点'),(nrt,'条路线'),(len(B),'张圣经地理')])
    hero=f'''<section class="hero reveal hero-map"><span class="chip d">🗺️ 历史 · 地图 · 文化</span><h1>历史地图集：要理问答走过的路</h1><p class="lead">历史地图，一条主线：<b>改教的水流</b>在海德堡汇合 → 写成<span class="mk-k">安慰之书</span> → 被<b>难民</b>带往北方 → 在<b>多特</b>成为合一信条。每张地图都配有一幅<b>概念示意图</b>（动画路线）和一幅<b>实时交互地图</b>（全球可用，离线可退回）。</p><div class="kpi">{kpi}</div></section>'''
    ov=sec('m-overview','🧭','导览：导览：地图与故事线',callout('core','一句话','**谁写的**（作者路线）→ **从哪里来**（改教传播）→ **在什么处境写成**（1563 普法尔茨）→ **怎样传开**（难民之路）→ **怎样被确认**（多特大会）。')+atlas_cards(MD.MAPS)+f'<div class="card reveal" style="margin-top:14px"><h3 id="ov-lanes">📊 各图年代跨度（点击跳转）</h3><div class="chart mm">{lanes_chart(MD.MAPS)}</div></div>')
    order=['ref','uo','hd1563','pal','tyw','mig','dort','trans','today']
    body=hero+ov+''.join(map_section(MD.BY[k]) for k in order)+SRCNOTE+f'<div class="pager"><a href="history.html">⬅ 🗺️ 历史地理（时间线 · 人物 · 文化）</a><a class="r" href="geo-bible.html">📖 圣经地理 ➡</a></div>'+MAPJS('')
    page('maps.html','历史地图集',body,'海德堡要理问答历史地图集：1563 普法尔茨、宗教改革传播、乌尔西努与俄利维亚努、难民之路、多特大会代表')
    hb=f'''<section class="hero reveal hero-map"><span class="chip g">📖 圣经地理 · 圣约历史</span><h1>圣经地理：恩典之约走过的路</h1><p class="lead">要理问答的教义不是抽象的观念，而是神在<b>真实的时间与地点</b>中的作为：呼召亚伯拉罕、带领以色列出埃及、差遣保罗把福音传到罗马。四张地图：<span class="mk-k">约的记号</span>、<span class="mk-k">救赎在先、律法在后</span>、<span class="mk-k">福音的地点</span>、<span class="mk-k">基督藉道招聚教会</span>。</p></section>'''
    rows=''.join(f'<tr><td>{m["ico"]} <a href="#m-{m["id"]}">{esc(m["short"])}</a></td><td>{"、".join(ldlink(n,"") for n,_ in m["lds"])}</td><td>{esc(m["hook"])}</td></tr>' for m in B)
    ov2=sec('m-bov','🧭','导览：地图 × 主日',callout('core','原则','**先看整本圣经的救恩史，再看局部地点**：每个地点都服务于“神与他的百姓立约”这条主线。')+f'<div class="tbl"><table><thead><tr><th>地图</th><th>相关主日</th><th>记忆钩</th></tr></thead><tbody>{rows}</tbody></table></div>')
    bb=hb+ov2+''.join(map_section(m) for m in B)+SRCNOTE+'<div class="pager"><a href="bible.html">⬅ 📖 圣经神学与圣约</a><a class="r" href="maps.html">🗺️ 历史地图集 ➡</a></div>'+MAPJS('')
    page('geo-bible.html','圣经地理',bb,'与海德堡要理问答相关的圣经地理：亚伯拉罕、出埃及、保罗旅程')
    print('maps pages done',sum(len(mapsvg.concept(m)) for m in MD.MAPS)//1024,'KB svg')
def ld_block(n):
    """Compact map card for a Lord's Day page (first linked map gets a small static illustration)."""
    items=MD.LDMAP.get(n)
    if not items: return ''
    mid,why=items[0]; m=MD.BY[mid]; href=lambda m:f'../{"maps" if m["page"]=="maps" else "geo-bible"}.html#m-{m["id"]}'
    more=''.join(f'<a class="chip" href="{href(MD.BY[i])}">{MD.BY[i]["ico"]} {esc(MD.BY[i]["short"])}：{esc(w)}</a>' for i,w in items[1:])
    inner=(f'<div class="grid g2 ldgeo"><a class="card reveal mthumb" href="{href(m)}" aria-label="打开地图：{esc(m["title"])}">{mapsvg.illustrate(m,W=420,small=True,uid=m['id']+'-s')}</a>'
           f'<div class="card pan why reveal"><h3 id="geo-why">{m["ico"]} {esc(m["title"])}</h3>{callout("hist","历史",md(why+"。"))}<p>{md(m["core"])}</p><div class="btns"><a class="btn pri" href="{href(m)}">🗺️ 打开概念图 + 实时地图</a></div>{("<div class=tags style=margin-top:10px>"+more+"</div>") if more else ""}</div></div>')
    return sec('geo','🗺️','历史与地理：这一主日的舞台',inner)
if __name__=='__main__': build()
