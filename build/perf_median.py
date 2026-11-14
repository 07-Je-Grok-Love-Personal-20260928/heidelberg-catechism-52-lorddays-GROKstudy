"""Run perf6.py N times and write a median-of-N JSON with a 'runs' fps list on each key."""
import json,os,statistics,subprocess,sys,time
BASE=sys.argv[1]; OUT=sys.argv[2]; N=int(sys.argv[3]) if len(sys.argv)>3 else 3
PAGES=sys.argv[4] if len(sys.argv)>4 else 'index.html,ld/01.html,ld/34.html,texts/hc-2.html,history.html,memory.html,maps.html,geo-bible.html,marks.html,compare.html,bible.html,lorddays.html'
script=os.path.join(os.path.dirname(os.path.abspath(__file__)),'perf6.py')
tmpdir=os.path.dirname(os.path.abspath(OUT)) or '.'
runs=[]
t0=time.time()
for i in range(N):
    part=os.path.join(tmpdir,f'.perf_run_{i}.json')
    print(f'=== run {i+1}/{N} BASE={BASE} ===',flush=True)
    env=os.environ.copy()
    subprocess.check_call([sys.executable,script,BASE,part,PAGES],env=env)
    runs.append(json.load(open(part)))
# median by fps for each key; other numeric fields also median; keep all fps in 'runs'
keys=list(runs[0].keys())
out={}
for k in keys:
    recs=[r[k] for r in runs]
    recs_s=sorted(recs,key=lambda x:x['fps'])
    mid=recs_s[len(recs_s)//2] if len(recs_s)%2 else recs_s[len(recs_s)//2-1]  # consistent with "middle of 3"
    # use statistical median for numeric, mid record as base
    y=dict(mid)
    y['runs']=[r['fps'] for r in recs]
    y['fps']=statistics.median(y['runs'])
    if isinstance(y['fps'],float) and y['fps'].is_integer(): y['fps']=int(y['fps']) if False else round(y['fps'],1)
    else: y['fps']=round(float(y['fps']),1)
    for field in ('p95','long50','task_ms','style_ms','layout_ms','script_ms','paint_ms','dom','scrolled'):
        if field in mid:
            vals=[r[field] for r in recs]
            y[field]=statistics.median(vals)
            if field in ('long50','task_ms','style_ms','layout_ms','script_ms','paint_ms','dom','scrolled'):
                y[field]=int(round(y[field])) if field!='p95' else y[field]
            if field=='p95': y[field]=round(float(statistics.median(vals)),1)
    out[k]=y
    print(k,'median',y['fps'],'runs',y['runs'],flush=True)
json.dump(out,open(OUT,'w'),indent=1)
print('wrote',OUT,'in',int(time.time()-t0),'s')
