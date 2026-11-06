from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
def offcap(w,mode):return 2*(w//4) if mode==1 else w//2
def ownmax(w,f,mode):return 0 if f==0 else (w//2-1 if mode==2 else w//2)
keys=set();branches=0
for support in(11,12):
    profiles={}
    for line in(HERE/f's{support}_after_two_heavy_own.txt').read_text().splitlines():
        t=list(map(int,line.split()));profiles[t[0]]=[(f,w) for f,w,n in zip(t[3::3],t[4::3],t[5::3]) for _ in range(n)]
    for line in(HERE/f'S{support}_OWN_PERIODIC_CANDIDATES.jsonl').read_text().splitlines():
        c=json.loads(line);source=profiles[c['parent_id']]
        for b in c['branches']:
            branches+=1;left=dict(zip(range(4,20,2),b['periodic_counts']));rows=[]
            for f,w in source:
                mode=0
                if f and w%2==0:
                    if w==2:mode=1
                    else:
                        mode=1 if left[w]>0 else 2
                        if mode==1:left[w]-=1
                rows.append((w,f,mode))
            assert not any(left.values())
            ell=b['cutoff'];channel=b['channel'];hs=[(offcap(w,mode),int(mode==1)) for w,f,mode in rows if offcap(w,mode)>ell]
            for w,f,mode in rows:
                ns=hs.copy();el=ell
                if offcap(w,mode)>ell:ns.remove((offcap(w,mode),int(mode==1)));el=0
                if mode!=1:ns=[(q,0) for q,period in ns]
                ns=tuple(sorted(ns,key=lambda x:(x[1],x[0])));keys.add((w,f,mode,el,channel,ns))
            if channel==0:
                ns=tuple(sorted((ownmax(w,f,mode),0) for w,f,mode in rows if f and offcap(w,mode)>ell));keys.add((19,-1,0,0,0,ns))
with(HERE/'OWN_PERIODIC_DUAL_KEYS.txt').open('w') as f:
    for w,flag,mode,ell,channel,ns in sorted(keys):f.write(' '.join(map(str,(w,flag,mode,ell,channel,len(ns),*(x for q in ns for x in q))))+'\n')
print(json.dumps({'candidate_branches':branches,'local_keys':len(keys)}))
