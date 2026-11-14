"""Run cpuf.py for v9 (first base) vs v10 (second) and write a median JSON."""
import json,os,re,statistics,subprocess,sys
script=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cpuf.py')
BASES=sys.argv[1]  # v9|v10
PROFN=sys.argv[2]
PAGES=sys.argv[3]
REPS=sys.argv[4] if len(sys.argv)>4 else '3'
OUT=sys.argv[5] if len(sys.argv)>5 else 'cpuf_out.json'
print('RUN',BASES,PROFN,PAGES,REPS,flush=True)
proc=subprocess.run([sys.executable,script,BASES,PROFN,PAGES,REPS],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
open(OUT+'.log','w').write(proc.stdout)
print(proc.stdout)
if proc.returncode:
    sys.exit(proc.returncode)
# parse SUM lines
# SUM index.html http://127.0.0.1:8780/ fps_est [..] cpu6 [..]
# actual: print('SUM',u,B[-6:],'fps_est',[...],'cpu6',[...])
# so: SUM index.html 8780/ fps_est [1,2,3] cpu6 [4,5,6]
bases=BASES.split('|')
# map last6 -> label
lab={bases[0][-6:]:'v9', bases[1][-6:]:'v10'}
out=json.load(open(OUT)) if os.path.exists(OUT) else {}
for line in proc.stdout.splitlines():
    if not line.startswith('SUM '): continue
    # SUM <page> <tag> fps_est <list> cpu6 <list>
    m=re.match(r'SUM (\S+) (\S+) fps_est (\[[^\]]+\]) cpu6 (\[[^\]]+\])', line)
    if not m:
        print('UNPARSED',line); continue
    u,tag,fps,cpu=m.group(1),m.group(2),eval(m.group(3)),eval(m.group(4))
    # long_est not in SUM line... extract from per-run prints if present
    key=f'{PROFN}/{u}'
    rec=out.get(key,{})
    label=lab.get(tag,'x')
    rec[label]=statistics.median(fps)
    rec[label+'cpu']=int(round(statistics.median(cpu)))
    rec[label+'_runs']=fps
    rec[label+'cpu_runs']=cpu
    out[key]=rec
    print('MED',key,label,rec[label],fps,flush=True)
json.dump(out,open(OUT,'w'),indent=1)
print('wrote',OUT)
